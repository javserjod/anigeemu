from django.contrib import admin

# Register your models here.
from quiz.models import User, Game, Round


class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date_played', 'source',
                    'mode', 'n_questions', 'difficulty', 'daily_challenge', 'daily_challenge_number', 'daily_challenge_date')
    list_filter = ('user', 'source', 'mode', 'daily_challenge')
    search_fields = ('user__username', 'source', 'mode')
    ordering = ('-date_played',)


admin.site.register(User)
admin.site.register(Game, GameAdmin)
admin.site.register(Round)
