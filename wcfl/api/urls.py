from django.urls import path

from .views import players_list

urlpatterns = [
        path('players', players_list, name='players_list'),
        ]
