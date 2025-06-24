# aniGeemu
Guess the character or media from modified images while discovering new recommendations!

## Distinctiveness and Complexity
This project features an application with a completely different functionality and purpose from the already implemented on the previous projects during the course. It is not a reskin for the Google Search interface, a simple Wikipedia nor an e-commerce web page. Not even a mailing system or a social network where users can exchange messages. I tried to differentiate from other final projects that I have come across on the internet, too. I decided to take a different path at the same time I developed something that people, besides me, could enjoy, with no utility other than having fun and also discovering new recommendations.

The project I'm submitting consists of a guessing game. The user is shown a different set of images, one by one, each of them having a visual effect that hinders the task, corresponding to anime or manga culture. User should submit a guess from a list of suggestions printed in real time as they write, whether it's a character's name or a media title. When the round is done,  the assumption is checked, adding a point in case of success, and related information is depicted underneath, which could discover the user a new product to consume in the future or even just to remember some curious facts. All the information is fetched from an external API (AniList) and the code is optimized to avoid CORS errors and excessive loading times. Furthermore, user has two possibilities: creating a private game, in which they must state all the configuration, leading to a more personalised experience, and a daily challenge, in which everyday a new preset game is added to a list, being the exactly same to all the users, so they can compare their results and show off. In addition, there's a profile section where all private games created are ordered, showing status, parameters or stats. The daily challenges section has a similar structure.

So, as it has been described, the project involves several aspects learnt throughout the course, combining them and going even further in difficulty terms. First of all, the basic structure has been programmed from scratch, as no initial template was given for the app: from what the user get to see (HTML, CSS, Bootstrap) to the logic behind (JS, Python) and databases (models). The application is constantly making API calls both to the backend and AniList Server' endpoint URLs. For the latter, I had to read the pertinent documentation in order to make the correct calls and consume the information received, which led to successive event listeners triggers, database CRUD operations and exhaustive monitoring. As far as I could, I tried to rely on JS logic instead of Django render, so only certain sections were reloaded after an action and not the whole page. Also, some animations or transitions were programmed to improve UX. Other configurations were applied to make the resulting web page completely responsive in every device, in spite of their screen size, as checked with developer's tools. While programming, I decided to adopt some testing techniques I was comfortable with to obtain a product free of errors and cheat proof, mainly print statements, try-except or try-catch blocks, admin menu, network exchange messages, CSRF token... As a result, I consider this the most comprehensive and well-executed web project I have developed so far, and I’m genuinely satisfied with the outcome!



## Files
All of the new files were created inside the quiz folder. I also modified the urls.py located in capstone, so it now refers to the urls from the quiz application thanks to the include keyword, just as explained during the course.



### HTML
The html files are located in the templates\quiz folder, which is composed of:

- components
    - daily_challenge_card.html : the structure of the daily challenges cards arranged in the Daily Challenges section, depicting all the parameters randomly selected (although the same for all the users thanks to a seed): game mode, difficulty level and source. Also adds the day and number of the challenge, the status (number of round played out of the total) and the current success rate. When the challenge is completed, it will be coloured in green if passed (>50% success rate) or red if failed (<50%).
    - game_card.html : follows a similar structure to the daily challenge cards, but particularized to the private games created by an user, all arranged on the Profile section and showing: unique id as title, a Delete button, gamemode and difficulty selected, and also status and success rate.
- gamemodes
    - guess_image.html : contains the structure of a game (both created game and daily challenge), showing the current round (with unrevealed results) or the details of a previous round. 
    
        - An scoreboard is printed at the top, showing with squares all the rounds the current game is composed of and with a colour indicating the round state: grey for PENDING, green for CORRECT and red for WRONG. User can click them to navigate between rounds, although only the direct next pending round is the only accessible pending round, after completing the current pending round (which is blinking). 
    
        - Under the scoreboard, there's a round title block where additional buttons to navigate to previous and next rounds are embedded. They only appear when possible.

        - Then, the round image is shown. When the round being looked at is a previous round (not pending, already solved), the user can see the original image and click it to toggle the visual modifications. If the round is the current pending round, user can't click it, just watch the modified image.

        - Next, if the round is still to be guessed, two buttons appear: left one, to skip the round, counting as error, and right one, to submit a guess. The mentioned guess is selected in the underneath text input. When user starts writing on it, a dropdown selector appears with main coincidences (information consumed from AniList API). User must click on one of them in order to submit.

        - If the round was completed, either CORRECT or WRONG, a pertinent text appears instead of the previous block, revealing correct answer. It is followed by a line with alternative titles/names and a container with most relevant information related to the picture subject, both received from a JS file. If it was a cover image (meaning official art of an anime or manga), a description, year, genres, average score, format, episodes, favourites and popularity should be printed (if they exist). In the case it was a character image, a description, gender, age and favourites should be shown, followed with the arranged character media participations cards, which are clickable and redirect to the media page.

- daily_challenge_list.html : arranges all the existing daily challenges until today, from newest to oldest. Uses a Paginator.

- game_configuration.html : allows the user to select preferences for a custom game. It is a form where they can choose a source (ANIME or MANGA), the gamemode (Character image or Cover Image), the updated genres (whose options are fetched from AniList so no Exception in genre will be made in future API calls in this game, also removing +18 categories), the number of question (limited from 1 to 50, with a range input or a regular input), and the difficulty level (same format as number of questions, but from 1 to 10). Finally a button to start the game is rendered. The genre selection also includes a Select All and Unselect All buttons.

- home.html : brief description of the page. If user is not logged in, shows two buttons: one for Login and one for Register. If user is logged in, proposes the two available options with two buttons: Game Configuration (custom game) and Daily Challenges, and also added a ko-fi iframe.

- layout.html : the file all the other files extend. 

    - Contains the title of the page, the link with Bootstrap 5 and Bootstraps Icons, the connection to the CSS file (style.css), the insertion of all the JS used in the development, a meta element with the CSRF token needed to make fetch calls from some JS files, and a meta viewport for responsive design. 

    - Apart from that, includes the Navbar. When user is logged-in, it is made up of the project name on the left and all the links to the pages of the app: Home, Game Configuration, Daily Challenge, Profile and Logout. If user is not logged-in, only contains the project name, and links to login and register views. When the app is running on a smaller device, all those links are compressed inside a button, which when clicked, shows all the pertinent links in a column format.

    - There is also a footer indicating the origin of the data, which is AniList.

- login.html : standard login page. User must write down an username and a password already inserted in the database and click on the Login button. A link to the register page is also added.

- profile.html : the page where all the private games with custom settings created by an user are gathered. They are arranged from newest to oldest. Like the Daily Challenges page, also uses a Paginator.

- register.html : standard register page. User must fill out a form with unique username, unique email address, password and a confirmation of the password, and then submit it with a Register button. A link to the login page is also added. 

### CSS
- styles.css : contains some of the CSS styling used, located inside the static\quiz folder. The rest was added inline with the HTML, whenever I found it more comfortable. Also, I included a few animations. Anyway, I mostly relied on Bootstrap classes. Inside this file, you can find: general containers (style), control cards and option cards from the game Configuration page (style and animations like rotate-select, hover), scoreboard (style, blinker animation), user guess input (style, hover), image guessed (glowing) and additional fetched info (fade-in effect, hide spoilers) from in-game page, and history (style, transitions when deleted, hover) from Profile page.

### Python
- admin.py : apart from registering all the models for the admin site, I decided to extend the monitoring of the Game class by adding GameAdmin, so it is easier to distinguish between daily challenges and custom games, date of creation, user, etc.
- apps.py
- models.py : contains the classes that will be mapped to SQL tables thanks to ORM. I decided to create three reasonable classes:
    - User : inherits from AbstractUser class. Simply redefines an \_\_str\_\_ method to print the object/entry as the username.
    - Game : the model that will store all the information from any game. It's columns are:
        - user : foreign key to user, also with related name.
        - score : the current score of the game.
        - date_played : stores the date when the game is created.
        - source : whether the game employs MANGA or ANIME as media type.
        - mode : Character Image or Cover Image.
        - genres : a string with all the genres available in AniList, comma-separated.
        - n_questions : the number of questions/rounds the game has.
        - difficulty : the level of difficulty of the game.
        - daily_challenge : boolean indicating if the game is a daily challenge or not (custom game).
        - daily_challenge_number : an ordinal to refer a daily challenge.
        - daily_challenge_date : the date of the daily challenge.

        Also created some methods:
        - \_\_str\_\_ : print game object as a string, considering if it's a daily challenge or not.
        - current_round : returns de current round, which is the first round with a pending state.
        - is_finished : returns a boolean indicating if the game is finished, that is to say, if there are no more pending rounds.
        - mean_score : returns the current mean score of a game, or empty string if not played any round yet.
        - used_id : checks if a round image has already been shown in the same game since its id (useful to prevent repeated rounds when fetching).
    
    - Round : each guessing round inside a game. Its columns are:
        - game : the game a round is a part of, also includes a related name.
        - number : the round number.
        - state : whether the round is PENDING, CORRECT or WRONG.
        - last_fetch : register of the time a round info was fetched.
        - db_entry_id : id of the fetched entry in the AniList DB.
        - image_url : stores the fetched entry's image URL.
        - modified_image : a modified version of the fetched image as a base64 string.
        - user_answer : the answer submitted by the user.
        - correct_answer : the real, correct answer for the entry fecthed from AniList (character's name or media title).

        Also a \_\_str\_\_ method to print the Round object as the round's number plus game id.

- tests.py : unused

- urls.py : includes all the URL accessible by the user and endpoints for backend actions.
    - "register" : URL where user can register.
    - "login" : URL where user can log in.
    - "logout" : : URL where user can log out.
    - "profile/\<str:username>" : URL where all the custom games of the mentioned username are arranged. Only accessible by the owner.
    - "game_configuration" : URL where the user can configure their own custom game.
    - "game/\<int:game_id>" : URL where the user is playing the current round of the game with the mentioned id. Only accessible by the owner.
    - "skip_round/\<int:game_id>" : endpoint accessed by the backend to skip the current round of the game with mentioned id, action triggered when user clicks Skip button.
    - "game/\<int:game_id>/\<int:round_number>": URL where user can inspect the result and additional information for a non pending round with the mentioned round number, for the game with the mentioned id.
    - "delete_game/\<int:game_id>" : endpoint accessed by the backend to delete the game whose card was clicked in the profile page.
    - "get_anilist_data/" : endpoint accessed from a JS file, which is triggered when detailing a non pending round. So a function in the backend is called, which, in turn, makes an API call to the Anilist server to fetch data, then goes back all the way to the frontend. The call from JS to our own backend is done to prevent CORS error for fetching too much on the client-side.
    - "daily_challenge" : just like the profile URL, but with the daily challenges, which are global to all the users, but not their progression on those.

- views.py : contains all the functions called when accessing certains URLs and also some others utility functions. Global constant variables are defined too to nerf or buff the difficulty.
    - home : 
        - GET -> renders the Home page.
    - register :
        - GET -> renders the Register page.
        - POST -> create a new User in the database from the given parameters (username, email, password, password confirmation), if correct.
    - login_view :
        - POST -> authenticates and logs in an user, if username-password combination is correct. Then redirects to Home page.
    - logout_view -> logs out the user and redirects to Home page.
    - profile : 
        - GET -> renders Profile page, passing as context the user and a page object (paginator) with all the user's games ordered from newest to oldest.
    - game_configuration :
        - GET -> renders Game Configuration page.
        - POST -> create a Game from the received parameters (user, source, mode, genres, n_qeustions and difficulty). Adds n_questions Round objects to that Game, all with the PENDING state and asigning them a number. The redirects to the in-game interface with the Game id as context.
    - game_update : in-game interface management
        - GET -> renders the in-game interface. 
            Before that, it is necessary to make some adjustments. With the only parameter received, the Game id, we obtain its source, genres, difficulty and current round. 
            
            We check if the Game is a daily challenge: if so, apply certain seed, if not, reset to the random seed.

            Then, after ensuring the gamemode is valid, we check if the current round already contains an image. 
            If so, it means we don't have to assign it an AniList entry, so we simply render guess_image.html with context (game, n_rounds, all its rounds and the modified image in base64 string format). If not, wait a cooldown and try to fetch from AniList, allowing some attempts in case of fecthing error (sometimes there are no valid results given certain source, genre and difficulty/page). Two other functions handle the mentioned AniList fetching, one for each mode: get_cover_image and get_character_image. If there is success in the retrieval, the image is modified with another function and converted to base64 string. Then all the empty attributes from the current round Object are filled, and we are redirected to the in-game interface with the same context as at the beginning of this paragraph.
        
        - POST -> user submits an answer. Then just compare the correct answer fetched before from AniList (now in our DB) for the current round with the user's guess. If correct, change round state to CORRECT and increase score. If wrong, simply save state to WRONG. Then redirect to the in-game interface, but through the game_round_details function for the just played round, revealing to the user if there was success and all the additional information.

    - skip_round : skips the current round of the game, saving a WRONG string in state and redirecting to game_round_details of that precise round.

    - game_round_details :
        - GET -> given a Game id and a Round number, checks if the round isn't PENDING, that is to say, if the round has already been solved. If not, redirects to game_update function. If so, renders in-game interface but with round_detailed as context, which indicates that we are in the detailing mode, apart from game, n_rounds, rounds, and both image_url and modified_image (to compare them).
    
    - delete_game :
        - POST -> delete a Game from its id. It is called from a JS file, so instead of rendering the whole page, it sends the changes to that JS file as JsonResponse. It checks if a game from the next page of the Paginator exists, in order to move it to the current page.

    - get_cover_image : makes an API call to the AniList DB to obtain a media entry. A query is constructed according to the documentation and sent via requests library. Just one random genre is picked from the user selected list. Also the difficulty selected by the user is used to set a page (later pages have less popular results, so the more difficult is to guess the correct answer). A query limit has been imposed to not saturate the AniList server. When we obtain an entry with a valid image, title and unused id (meaning it is a new entry for the current game), return it. This is only called from the previous game_update function.

    - get_character_image : the analogue of the previous one, but for characters. This one has to go one step further: apart from the random genre and random page, which lead us to a media list where we pick a random media, we need a random page of that media where we get a random character entry. Ensure that its image is valid (exists and also is not the placeholder image, which would make the round impossible to guess), its name is valid and hasn't been used in this Game.

    - get_anilist_data : 
        - POST -> also fetches information from AniList, this time additional information for an already built and played Round. Differentiate between the query of a media and the query of a character (different information will be needed). Return as JsonResponse. This is called from a JS file`, and not made directly in that JS file, in order to prevent CORS errors.

    - daily_challenge_list: calls the create_daily_challenge once for day since the initial date for daily challenge until today. Then returns it as context in Paginator format, next to the User object, when rendering Daily Challenge page.

    - set_seed_for_daily_challenge : sets certain seed when a daily challenge is being created or played. The seed is constructed with that daily challenge's date plus the round number, so there's variability in the query inside a same Game, although being the exact same to all the users as expected.

    - create_daily_challenge : creates a Game object for the current user, if doesn't exist already for that date, with the given date and setting daily_challenge as True. Inside of it sets a seed just before randomly selecting a source, mode, and difficulty. Also create its Round objects.

    - is_placeholder_image : checks if the given image is an Anilist's placeholder image, by comparing mean colors of both images with a certain tolerance. We already have the placeholder mean color.

    - image_random_modify: executes one of the 5 functions dedicated to add a certain modification to the image to hinder the guess.

    - blur_image_from_url: applies Gaussian blur to an image given a kernel size.

    - pixelate_image_from_url: pixelates an image given a kernel size.

    - invert_image_from_url: inverts the color of an image.

    - noise_posterize_image_from_url: adds noise to an image and then posterize it with the given clusters.

    - scramble_image_from_url: decompose the image in blocks and randomly arrange them, maintaining the original size.

    - genres_to_list : convert the stored string containing all the genres comma-separatedly to a list.


### JavaScript
JS files were added inside the static\quiz folder.
- alternate_images.js : add glow class to the image depending the result of the guess and allow a click on it to toggle between original image and modified image.
- anti_spam_new_round_fetch.js : disables the Next button when the next round needs to be fetched once clicked for the first time, in order to prevent multiple clicks, which could lead to consecutive queries, and therefore, to a block from the server for rate limiting.
- autocomplete.js : adds content to the suggestions dropdown list while writing on the input above it. The suggestions appear when a substring or the whole string being written by the user is completely or partially one of the entries' names/titles or alternative names/titles. The suggestions are fetched almost in real time from Anilist from this exact JS file.

- delete_game.js : makes a POST request to the backend pertinent funtcion after detecting a click event on a Delete button for certain card. Then a delete-card-effect is added to its closest game card before removing it from the DOM. After that, the content is rearranged, filling the gap and adding once again all the click event listeners to the respective buttons.

- fetch_additional_info.js : adds a reveal effect to the original image on the in-game interface, when detailing a solved round. Makes POST requests to the backend's get_anilist_data, differentiating between Character Image and Cover Image gamemodes. When received, HTML is built with that information and added to the information container. Also, detects the markdown_spoiler class appended automatically by AniList and assign it a new class to make its content completely black, unreadable. Finally, only for the Character Image mode, renders the character's participations in different medias with their role on it.

- focus_image.js : autocenter or focus the images (original or modified) when detected on the DOM.

- game_config_selection.js : manages the styles of the selection cards in the Game Configuration page, adding or removing classes (mainly UX) when clicked and assigning the value to a hidden input, which will be sent when submitted the form. Also fetches all the available categories in AniList, adding a spinner while they are loading. The logic behind the Select All and Unselect All genres is controlled by this file too.


## How to run application
As every other previous project seen throughout the course, this apps runs with the command:

            python manage.py runserver

Then simply click on the URL on console.