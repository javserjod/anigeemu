from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):

    def __str__(self):
        return self.username


class Game(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='games')
    score = models.IntegerField(default=0)
    date_played = models.DateField(auto_now_add=True)

    source = models.CharField(max_length=50)
    mode = models.CharField(max_length=50)
    genres = models.JSONField(default=list)
    n_questions = models.IntegerField(default=10)
    difficulty = models.IntegerField(default=1)  # From 1 to 5

    # Used for daily challenges
    daily_challenge = models.BooleanField(default=False)
    daily_challenge_number = models.IntegerField(
        blank=True, null=True)
    daily_challenge_date = models.DateField(
        blank=True, null=True)

    def __str__(self):
        if self.daily_challenge:
            return f"Daily Game #{self.daily_challenge_number} from {self.user.username}"
        else:
            return f"Game #{self.id} from {self.user.username}"

    def current_round(self):
        return self.rounds.filter(state=Round.PENDING).first()

    def is_finished(self):
        return not self.rounds.filter(state=Round.PENDING).exists()

    def mean_score(self):
        rounds = self.rounds.all()
        correct_rounds = rounds.filter(state=Round.CORRECT).count()
        wrong_rounds = rounds.filter(state=Round.WRONG).count()
        if correct_rounds + wrong_rounds == 0:
            return ""
        return correct_rounds / (correct_rounds + wrong_rounds) * 100

    def used_id(self, id):
        """
        Checks if id is already used in rounds of this game.
        Returns True if the id is already used, False otherwise.
        """
        return self.rounds.filter(db_entry_id=id).exists()


class Round(models.Model):
    PENDING = 'PENDING'
    CORRECT = 'CORRECT'
    WRONG = 'WRONG'
    ROUND_STATES = [
        (PENDING, 'Pending'),
        (CORRECT, 'Correct'),
        (WRONG, 'Wrong'),
    ]
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='rounds')
    number = models.IntegerField()
    state = models.CharField(
        max_length=10, choices=ROUND_STATES, default='PENDING')
    last_fetch = models.DateTimeField(null=True, blank=True)

    db_entry_id = models.IntegerField(blank=True, null=True)
    image_url = models.URLField(max_length=200, blank=True, null=True)
    modified_image = models.TextField(blank=True, null=True)

    user_answer = models.CharField(max_length=200, blank=True, null=True)
    correct_answer = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Round {self.number} of Game #{self.game.id}"
