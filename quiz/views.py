from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required

from quiz.models import User, Game, Round
import requests
import random
import numpy as np
import cv2
import base64
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, date
from django.template.loader import render_to_string
from PIL import Image
from io import BytesIO
import json

# Number of games to display per page in user's profile
GAMES_PER_PAGE = 12

# Maximum attempts to fetch a valid page
MAX_ATTEMPTS_PAGES = 5

# Maximum attempts to fetch a valid image or character according to the parameters given by the user FROM A CHOOSEN PAGE
MAX_ATTEMPTS_FROM_PAGE = 10

# Cooldown time in seconds for fetching a new image or character
FETCH_COOLDOWN_SECONDS = 5

# -------- DIFFICULTY VARIABLES --------
# Number of media items to fetch from Anilist perPage. Maximum is 50. Try to reduce due to the CORS error when fetching images. Also the number of characters perPage from a media. The bigger, the more difficult the game will be, as more media and characters will be available to be selected.
N_FETCHED_ELEMENTS = 7

# Value to adjust the position of the pages that may be fetched from Anilist. The bigger, later pages (less popular) will have more probability to be fetched. Less than 7 for securing a page with enough results. Adjust looking at N_FETCHED_ELEMENTS.
DIFFICULTY_RATIO_MEDIA = 3

# Value to adjust the possible characters prone to be selected, after ordering by favourites inside of the media. This value multiplies the difficulty level to get a maximum index to slice the media list, creating a range of possible characters to be selected. The bigger, the more characters will be available to be selected. Less than 5 for securing a character with enough results. Adjust looking at N_FETCHED_ELEMENTS.
DIFFICULTY_RATIO_CHARACTERS = 0.5

# --------- DAILY CHALLENGE VARIABLES ---------
ANILIST_GENRES = ['Action,Adventure,Comedy,Drama,Ecchi,Fantasy,Horror,Mahou Shoujo,Mecha,Music,Mystery,Psychological,Romance,Sci-Fi,Slice of Life,Sports,Supernatural,Thriller']

N_QUESTIONS_DAILY_CHALLENGE = 20

POSSIBLE_DIFFICULTIES_DAILY_CHALLENGE = [1, 2, 3, 4, 5, 6]

# The first date for the daily challenge. Y, M, D format.
FIRST_DATE_DAILY_CHALLENGE = date(2025, 6, 1)


def home(request):
    if request.method == "GET":
        return render(request, "quiz/home.html")


def register(request):
    if request.method == "GET":
        return render(request, "quiz/register.html")

    elif request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")
        if password != confirmation:
            return render(request, "quiz/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
            )
            user.save()
        except IntegrityError:
            return render(request, "quiz/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("home"))


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("home"))
        else:
            return render(request, "quiz/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "quiz/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))


@login_required
def profile(request, username):
    if request.method == "GET":

        user = get_object_or_404(User, username=username)
        all_games = Game.objects.filter(
            user=user, daily_challenge=False).order_by('-date_played')

        paginator = Paginator(all_games, GAMES_PER_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "quiz/profile.html", {
            "user": user,
            "page_obj": page_obj,
        })


@login_required
def game_configuration(request):
    if request.method == "GET":
        return render(request, "quiz/game_configuration.html")
    elif request.method == "POST":
        # create a new game instance
        try:
            game = Game.objects.create(
                user=request.user,
                source=request.POST.get("game_source"),
                mode=request.POST.get("game_mode"),
                genres=request.POST.getlist("game_genres"),
                n_questions=int(
                    request.POST.get("number_of_questions")),
                difficulty=int(request.POST.get("difficulty"))
            )

            for i in range(1, game.n_questions + 1):   # 1-based index
                # create a round for each question
                game.rounds.create(
                    number=i,
                    state="PENDING"
                )

            game.save()
            return HttpResponseRedirect(reverse("game_update", args=[game.id]))

        except IntegrityError:
            return render(request, "quiz/game_configuration.html", {
                "message": "Error creating game. Please try again."
            })


@login_required
def game_update(request, game_id):
    if request.method == "GET":

        game = get_object_or_404(Game, id=game_id, user=request.user)
        source = game.source
        genres = game.genres
        difficulty = game.difficulty
        current_round = game.current_round()

        if game.daily_challenge:
            # if the game is a daily challenge, set the seed for reproducibility, just in case
            set_seed_for_daily_challenge(
                game.daily_challenge_date, game.current_round().number)
        else:
            # if the game is not a daily challenge, set random seed for unpredictability
            random.seed()  # set a random seed for unpredictability

        # print(f"source: {source}, genres: {genres}, difficulty: {difficulty}")

        if game.mode in ["Cover Image", "Character Image"]:

            # image already assigned to the round -> just render the page
            if current_round.image_url:
                return render(request, "quiz/gamemodes/guess_image.html", {
                    "game": game,
                    "n_rounds": range(1, game.n_questions + 1),
                    "rounds": game.rounds.all(),
                    # "image_url": current_round.image_url,
                    "modified_image": current_round.modified_image
                })

            # no image assigned to the round -> fetch a new one
            else:
                now = timezone.now()

                if current_round.last_fetch and (now - current_round.last_fetch) < timedelta(seconds=FETCH_COOLDOWN_SECONDS):
                    return render(request, "quiz/gamemodes/guess_image.html", {
                        "game": game,
                        "n_rounds": range(1, game.n_questions + 1),
                        "rounds": game.rounds.all(),
                        "modified_image": current_round.modified_image
                    })
                else:
                    image_url, correct_answer, db_id = None, None, None
                    for i in range(MAX_ATTEMPTS_PAGES):
                        # sometimes errors occur when fetching images from Anilist (unknown cause)
                        try:
                            if game.mode == "Cover Image":
                                print("Fetching cover image...")
                                result = get_cover_image(
                                    source, genres, game, max(1, difficulty-i))
                            elif game.mode == "Character Image":
                                print("Fetching character image...")
                                result = get_character_image(
                                    source, genres, game, max(1, difficulty-i))

                            if result is None:
                                raise ValueError(
                                    f"No valid round found. Reducing difficulty from {difficulty} to {max(1, difficulty-i-1)} and trying again, just for this round.\n")
                            else:
                                image_url, correct_answer, db_id = result
                                break

                        except ValueError as e:
                            print(f"{e}")

                    if any([image_url is None, correct_answer is None, db_id is None]):
                        # game.delete()  # delete the game if no valid image found? better not... sometimes cancel is due to CORS
                        # no valid round found after maximum attempts
                        print("No valid found after maximum attempts.")
                        return render(request, "quiz/game_configuration.html", {"error_message": "No valid image found. Game cancelled. Please try again with less restrictive parameters or just wait for the DB to answer."})

                    modified_image = image_random_modify(image_url)

                    # save info for the current round
                    current_round.image_url = image_url
                    current_round.modified_image = modified_image
                    current_round.correct_answer = correct_answer
                    current_round.db_entry_id = db_id
                    current_round.last_fetch = now
                    current_round.save()

                    return render(request, "quiz/gamemodes/guess_image.html", {
                        "game": game,
                        "n_rounds": range(1, game.n_questions + 1),
                        "rounds": game.rounds.all(),
                        # "image_url": image_url,
                        "modified_image": modified_image,
                    })
        else:
            return HttpResponse(status=400)

    # POST request handling = user submitting an answer
    else:
        user_input = request.POST.get("user_input")
        game = get_object_or_404(Game, id=game_id, user=request.user)
        current_round = game.current_round()
        current_round.user_answer = user_input

        # if user tries to SUBMIT a round that is NOT ASSIGNED YET, redirect to game update (GET) (example: user goes back with browser and tries to submit an answer for an unassigned round - which answer has already being shown - although a past round is being displayed). if current round has been assigned but not revealed, will be counted as error, as it is not handled.
        if current_round.correct_answer is None:
            return HttpResponseRedirect(reverse("game_update", args=[game.id]))

        if user_input == current_round.correct_answer:
            current_round.state = 'CORRECT'
            current_round.save()  # save the round state

            game.score += 1  # increment score
            game.save()  # save the game score

        else:
            current_round.state = 'WRONG'
            current_round.save()

        return HttpResponseRedirect(reverse("game_round_details", args=[game.id, current_round.number]))


@login_required
def skip_round(request, game_id):
    """
    Skip the current round of the game.
    This will mark the current round as 'WRONG' and move to the next round.
    """
    game = get_object_or_404(Game, id=game_id, user=request.user)
    current_round = game.current_round()
    # if user tries to SKIP a round that is NOT ASSIGNED YET, redirect to game update (GET) (example: user goes back with browser and tries to skip an answer for an unassigned round - which answer has already being shown - although a past round is being displayed). if current round has been assigned but not revealed, will be counted as error, as it is not handled.
    if current_round.correct_answer is None:
        return HttpResponseRedirect(reverse("game_update", args=[game.id]))
    current_round.state = 'WRONG'
    current_round.save()

    return HttpResponseRedirect(reverse("game_round_details", args=[game.id, current_round.number]))


@login_required
def game_round_details(request, game_id, round_number):
    if request.method == "GET":
        game = get_object_or_404(Game, id=game_id, user=request.user)
        round = get_object_or_404(Round, game=game, number=round_number)

        # only if previous round (anti cheating)
        if round.state != Round.PENDING:
            return render(request, "quiz/gamemodes/guess_image.html", {
                "game": game,
                "n_rounds": range(1, game.n_questions + 1),
                "rounds": game.rounds.all(),
                "round_detailed": round,
                "image_url": round.image_url,
                "modified_image": round.modified_image,
            })
        # if user tries to access a round that is not finished yet
        else:
            return HttpResponseRedirect(reverse("game_update", args=[game.id]))


@login_required
def delete_game(request, game_id):
    if request.method == "POST":
        """
        Delete a game instance and all its associated rounds.
        If the game is deleted successfully, return the next game card to be displayed in that page.
        """
        try:
            current_page = int(request.GET.get("page", 1))  # parameter in URL
            next_page_first_index = current_page * GAMES_PER_PAGE
            next_game_qs = Game.objects.filter(user=request.user, daily_challenge=False).order_by(
                '-date_played')[next_page_first_index:next_page_first_index+1]   # not just index, but a slice, so in case there are no more games we don't get an IndexError
            next_game = next_game_qs[0] if next_game_qs else None

            print(f"Deleting game with ID: {game_id}")
            game = get_object_or_404(Game, id=game_id, user=request.user)
            game.delete()  # this will also delete all associated rounds

            # if there are more games to show from the next page
            if next_game:
                rendered = render_to_string(
                    "quiz/components/game_card.html", {'game': next_game}, request=request)
                return JsonResponse({"html": rendered}, status=200)
            else:
                return JsonResponse({"html": None}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def get_cover_image(source, genres, game, difficulty):
    """
    Fetch a random cover image from Anilist based on the source and genres.
    Returns the image URL and the title of the media (correct answer).
    """
    genres_list = genres_to_list(genres)
    random_genre = random.choice(genres_list)
    random_page = random.randint(1, np.ceil(
        difficulty * DIFFICULTY_RATIO_MEDIA))

    url = 'https://graphql.anilist.co'
    query = '''
    query ($page: Int, $perPage: Int, $type: MediaType, $genre: [String]) {
        Page(page: $page, perPage: $perPage) {
            media(type: $type, genre_in: $genre, sort: POPULARITY_DESC) {
                id
                title {
                    romaji
                }
                coverImage {
                    large
                }
            }
        }
    }
    '''
    variables = {
        "page": random_page,
        "perPage": N_FETCHED_ELEMENTS,
        "type": source.upper(),   # "ANIME" or "MANGA"
        "genre": random_genre,

    }
    try:
        response = requests.post(
            url, json={"query": query, "variables": variables})
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        media_list = data.get("data", {}).get("Page", {}).get("media", None)

        if not media_list:
            print("Empty or missing media list. Response:", data)
            return None

        for _ in range(MAX_ATTEMPTS_FROM_PAGE):
            random_media = random.choice(
                media_list)   # Get a random media item

            img = random_media.get("coverImage", {}).get("large")
            title = random_media.get("title", {}).get("romaji")
            id = random_media.get("id")
            if img and title and (not game.used_id(id)):
                print(
                    f"\nCover image selected from {title}, located in the page {random_page} ({N_FETCHED_ELEMENTS} elem./page, so position close to {random_page*N_FETCHED_ELEMENTS}) of the popularity rank.\n")
                return (img, title, id)

        raise ValueError("No valid media found after maximum attempts.")

    except (KeyError, TypeError, requests.RequestException, ValueError) as e:
        print(f"Error fetching or parsing Anilist data: {e}")
        return None


def get_character_image(source, genres, game, difficulty):
    """
    Fetch a random character image from a random media from Anilist based on the source, random genre from the selected and chosen difficulty.
    When using seed, the same character will be selected for the same game configuration, so the game is reproducible.
    Returns the image URL of a character from a random media item, the character's name (correct answer), its ID in AniList for future use and other additional info.
    """
    genres_list = genres_to_list(genres)
    random_genre = random.choice(genres_list)
    random_page = random.randint(1, np.ceil(
        difficulty * DIFFICULTY_RATIO_MEDIA))
    random_page_char = random.randint(
        1, np.ceil(difficulty * DIFFICULTY_RATIO_CHARACTERS))

    url = "https://graphql.anilist.co"
    query = '''
    query ($page: Int, $pageChar: Int, $type: MediaType, $genre: [String], $perPage: Int) {
        Page(page: $page, perPage: $perPage) {
            media(type: $type, genre_in: $genre, sort: POPULARITY_DESC) {
                favourites
                title {
                    romaji
                }
                characters(page: $pageChar, perPage: $perPage, sort: FAVOURITES_DESC) {
                    nodes {
                        id
                        name {
                            full
                        }
                        image {
                            large
                        }
                        favourites
                    }
                }
            }
        }
    }
    '''
    variables = {
        "page": random_page,
        "pageChar": random_page_char,
        "perPage": N_FETCHED_ELEMENTS,
        "type": source.upper(),  # "ANIME" or "MANGA"
        "genre": random_genre,
    }

    try:
        response = requests.post(
            url, json={"query": query, "variables": variables})
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        media_list = data.get("data", {}).get("Page", {}).get("media", [])

        if not media_list:
            print("Empty or missing media list. Response:", data)
            return None

        for _ in range(MAX_ATTEMPTS_FROM_PAGE):
            media = random.choice(media_list)
            # print(media)
            characters = media.get("characters", {}).get("nodes", [])
            if not characters:
                continue

            print(f"Fetched {len(characters)} characters from media.")
            # choose 1 character from the N_FETCHED_ELEMENTS
            character = random.choice(characters)

            img = character.get("image", {}).get("large")
            name = character.get("name", {}).get("full")
            id = character.get("id")

            # if character not used in the game before
            if name and (not game.used_id(id)):
                # if image is not a placeholder image
                if img and (not is_placeholder_image(img)):
                    print(
                        f"\nSelected from {media.get('title', {}).get('romaji')} the character in the page {random_page_char} ({N_FETCHED_ELEMENTS} elem./page, so position close to {random_page_char*N_FETCHED_ELEMENTS}) of the popularity rank, with {character.get('favourites')} favourites.\n")
                    return (img, name, id)
            else:
                print(f"Character already used this game: {name}")

        raise ValueError("No valid character found after maximum attempts.")

    except (KeyError, TypeError, requests.RequestException, ValueError) as e:
        print(f"Error fetching or parsing Anilist data: {e}")
        return None


@login_required
def get_anilist_data(request):
    '''
    Initially implemented in JS to fetch additional info from Anilist API, but CORS policy caused issues. Moved to Django view.
    Fetch additional info from Anilist API based on the media ID.
    Returns a JSON response with the media title, description, and other relevant info.
    '''
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    try:
        data = json.loads(request.body)
        query_type = data.get("type")
        anilist_id = data.get("id")

        if query_type == "Media":
            query = '''
            query ($id: Int) {
                Media(id: $id) {
                    id
                    title {
                        romaji
                        english
                    }
                    description(asHtml: true)
                    episodes
                    volumes
                    genres
                    averageScore
                    seasonYear
                    format
                    favourites
                    popularity
                    siteUrl
                }
            }'''
        elif query_type == "Character":
            query = '''
            query ($id: Int) {
                Character(id: $id) {
                    name {
                        full
                        alternative
                    }
                    age
                    gender
                    description(asHtml: true)
                    favourites
                    siteUrl
                    media(perPage: 30, sort: POPULARITY_DESC) {
                        edges {
                            characterRole
                            node {
                                id
                                title {
                                    romaji
                                    english
                                }
                                seasonYear
                                siteUrl
                                format
                                coverImage {
                                    large
                                }
                            }
                        }
                    }
                }
            }'''
        else:
            return JsonResponse({"error": "Invalid type."}, status=400)

        response = requests.post(
            'https://graphql.anilist.co/',
            json={'query': query, 'variables': {'id': anilist_id}},
            headers={'Content-Type': 'application/json'}
        )
        return JsonResponse(response.json())

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def daily_challenge_list(request):
    # for day since FIRST_DATE_DAILY_CHALLENGE, generate a daily challenge for each day if there is not one already
    for n in range((date.today() - FIRST_DATE_DAILY_CHALLENGE).days + 1):
        day = FIRST_DATE_DAILY_CHALLENGE + timedelta(days=n)
        create_daily_challenge(request, day, n+1)

    daily_challenges = Game.objects.filter(
        user=request.user, daily_challenge=True).order_by('-daily_challenge_date')

    paginator = Paginator(daily_challenges, GAMES_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "quiz/daily_challenge_list.html", {
        "user": request.user,
        "page_obj": page_obj,
    })


def set_seed_for_daily_challenge(date, round_number=1):
    """
    Set a seed for the daily challenge based on the date.
    Add also a variation for round numebr, because otherwise the same seed will be used for all rounds of the same daily challenge: the same page, same image, same character, etc (although it was controlled by try except and attempts, avoiding exact same characters/covers)
    This function is used to ensure that the daily challenge is reproducible.
    """
    seed_date = int(date.strftime("%Y%m%d"))
    seed_value = f"{seed_date}_{round_number}"
    random.seed(seed_value)
    print(
        f"Seed set for daily challenge on {date}, round {round_number}: {seed_value}")


def create_daily_challenge(request, date, number):
    """
    Generate a new daily challenge for date.
    This function should create a new DailyChallenge instance with the current date and a seed based on the date.
    """
    try:
        if not Game.objects.filter(
            user=request.user,
            daily_challenge_date=date,
            daily_challenge=True
        ).exists():
            # then create it for that date and assign it to the user
            print(f"\nCreating daily challenge for {date}...")

            set_seed_for_daily_challenge(date)

            game = Game.objects.create(
                daily_challenge=True,
                daily_challenge_date=date,
                daily_challenge_number=number,

                user=request.user,
                source=random.choice(["ANIME", "MANGA"]),
                mode=random.choice(["Character Image", "Cover Image"]),
                genres=ANILIST_GENRES,
                n_questions=N_QUESTIONS_DAILY_CHALLENGE,
                difficulty=random.choice(
                    POSSIBLE_DIFFICULTIES_DAILY_CHALLENGE),
            )

            for i in range(1, game.n_questions + 1):   # 1-based index
                # create a round for each question
                game.rounds.create(
                    number=i,
                    state="PENDING"
                )

            game.save()
            print(f"Daily challenge created for {date}.\n")

        else:   # game daily challenge for certain date already exists for that user
            print(f"Daily challenge for {date} already exists.\n")

    except Exception as e:
        print(f"Error creating or searching daily challenge for {date}: {e}")
        return render(request, "quiz/daily_challenge_list.html", {
            "message": "Error creating or searching daily challenge. Please try again."
        })


# other utility functions
#
# ----------------------------------------------
def is_placeholder_image(image_url, placeholder_mean_color=(39, 50, 78), tol=5):
    """
    Check if the image URL is a placeholder image.
    Returns True if it is a placeholder, False otherwise.
    tol is the tolerance for the mean color distance.
    The default placeholder mean color is a dark blue (39, 50, 78).
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
        mean_color = np.array(img).mean(axis=(0, 1))
        mean_color = np.array(mean_color)
        placeholder_mean_color = np.array(placeholder_mean_color)
        # print(f"Mean color of the image: {mean_color}")
        # print(f"Placeholder mean color: {placeholder_mean_color}")
        distance = np.linalg.norm(mean_color - placeholder_mean_color)
        print(f"Distance from placeholder image mean color: {distance}")

        return distance < tol

    except Exception as e:
        print(f"Error checking placeholder image: {e}")
        return False


def image_random_modify(image_url):
    """
    Randomly modify an image from a URL.
    The modification can be either blurring, pixelating, inversion, noise+posterization and scrambling.
    Returns the modified image as a base64 string.
    """
    n = random.randint(1, 5)  # random number to choose the modification
    match n:
        case 1:
            return blur_image_from_url(image_url)
        case 2:
            return pixelate_image_from_url(image_url)
        case 3:
            return invert_image_from_url(image_url)
        case 4:
            return noise_posterize_image_from_url(image_url)
        case 5:
            return scramble_image_from_url(image_url)


def blur_image_from_url(image_url, kernel_size=(55, 55)):
    """
    Apply Gaussian blur to an image from a URL.
    Kernel size is a tuple (width, height) that defines the size of the Gaussian kernel. Each value should be odd and positive. The bigger the kernel, the more blurred the image will be.
    Returns the modified image as a base64 string.
    """
    response = requests.get(image_url)
    if response.status_code != 200:
        return HttpResponse(status=404)

    image_data = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    # apply Gaussian blur to the image
    # bigger kernel size means more blur
    blurred = cv2.GaussianBlur(image, kernel_size, 0)

    success, buffer = cv2.imencode('.jpg', blurred)
    if not success:
        return None

    # convert the image to base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"


def pixelate_image_from_url(image_url, kernel_size=(32, 32)):
    """
    Pixelate an image from a URL.
    Kernel size is a tuple (width, height) that defines the size of the pixelation, which is later resized to the original image size.
    Returns the modified image as a base64 string.
    """

    response = requests.get(image_url)
    if response.status_code != 200:
        return HttpResponse(status=404)

    image_data = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    height, width = image.shape[:2]
    # desired "pixelated" size, the smaller the size, harder the game
    w, h = kernel_size

    # resize image to "pixelated" size
    temp = cv2.resize(image, (w, h), interpolation=cv2.INTER_LINEAR)

    # go back to original size
    pixelated = cv2.resize(temp, (width, height),
                           interpolation=cv2.INTER_NEAREST)

    success, buffer = cv2.imencode('.jpg', pixelated)
    if not success:
        return None

    # convert the image to base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"


def invert_image_from_url(image_url):
    response = requests.get(image_url)
    if response.status_code != 200:
        return HttpResponse(status=404)

    image_data = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    inverted = cv2.bitwise_not(image)

    success, buffer = cv2.imencode('.jpg', inverted)
    if not success:
        return None

    # convert the image to base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"


def noise_posterize_image_from_url(image_url, noise_scale=100, n_colors=5):
    """
    Add noise and then posterize an image from a URL.
    n_colors is the number of colors to reduce the image to.
    Returns the modified image as a base64 string.
    """
    response = requests.get(image_url)
    if response.status_code != 200:
        return HttpResponse(status=404)

    image_data = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    # Add Gaussian noise
    noise = np.random.normal(
        loc=0, scale=noise_scale, size=image.shape).astype(np.int16)
    noisy_image = np.clip(image.astype(np.int16) +
                          noise, 0, 255).astype(np.uint8)

    # Convert to LAB color space
    lab_image = cv2.cvtColor(noisy_image, cv2.COLOR_BGR2Lab)
    Z = lab_image.reshape((-1, 3)).astype(np.float32)

    # Apply k-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(
        Z, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Convert back to original shape
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
    quantized_image = quantized.reshape(lab_image.shape)

    # Convert back to BGR color space
    posterized_image = cv2.cvtColor(quantized_image, cv2.COLOR_Lab2BGR)

    success, buffer = cv2.imencode('.jpg', posterized_image)
    if not success:
        return None

    # Convert the image to base64
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{img_base64}"


def scramble_image_from_url(image_url, block_size=60):
    """
    Scramble an image from a URL by shuffling its blocks.
    block_size defines the size of the blocks to shuffle. The bigger the block size, the easier the game.
    Returns the modified image as a base64 string.
    """
    response = requests.get(image_url)
    if response.status_code != 200:
        return HttpResponse(status=404)

    image_data = np.frombuffer(response.content, np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    original_height, original_width = image.shape[:2]

    # Ensure dimensions are divisible by block_size
    resize_height = original_height - (original_height % block_size)
    resize_width = original_width - (original_width % block_size)
    resized_image = cv2.resize(image, (resize_width, resize_height))

    # Divide the image into blocks
    blocks = []
    for y in range(0, resize_height, block_size):
        for x in range(0, resize_width, block_size):
            block = resized_image[y:y+block_size, x:x+block_size]
            blocks.append(block)

    # Shuffle blocks
    np.random.shuffle(blocks)

    # Reconstruct the image from shuffled blocks
    scrambled = np.zeros_like(resized_image)
    idx = 0
    for y in range(0, resize_height, block_size):
        for x in range(0, resize_width, block_size):
            scrambled[y:y+block_size, x:x+block_size] = blocks[idx]
            idx += 1

    scrambled_resized = cv2.resize(
        scrambled, (original_width, original_height), interpolation=cv2.INTER_LINEAR)

    success, buffer = cv2.imencode('.jpg', scrambled_resized)
    if not success:
        return None

    img_base64 = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{img_base64}"


def genres_to_list(genres):
    """
    Convert a string with comma-separated genres into a list.
    Genres is saved in model as a unique String inside a list, so we need to split it.
    Return a list of genres.
    """
    return [genre for genre in genres[0].split(",")]
