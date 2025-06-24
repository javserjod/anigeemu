from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login_view"),
    path("logout", views.logout_view, name="logout_view"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("game_configuration", views.game_configuration, name="game_configuration"),
    path("game/<int:game_id>", views.game_update, name="game_update"),
    path("skip_round/<int:game_id>", views.skip_round, name="skip_round"),
    path("game/<int:game_id>/<int:round_number>",
         views.game_round_details, name="game_round_details"),
    path("delete_game/<int:game_id>", views.delete_game, name="delete_game"),
    path("get_anilist_data/", views.get_anilist_data, name='get_anilist_data'),
    path("daily_challenge",
         views.daily_challenge_list, name="daily_challenge_list"),


]
