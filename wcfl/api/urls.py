from django.urls import path

from .views import players_list, submit_squad, get_lineup, submit_transfer, opponent_lineup

urlpatterns = [
        path('players', players_list, name='players_list'),
        path('submitSquad', submit_squad, name='submit_squad'),
        path('lineup', get_lineup, name='get_lineup'),
	path('transfer', submit_transfer, name='submit_transfer'),
        path('oppLineup', opponent_lineup, name='opponent_lineup')
        ]
