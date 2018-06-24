from .models import Team, Player, Squad
from common.models import User, UserStat


def print_teams():
    teams = Team.objects.all()
    for team in teams:
        print(team)

def print_players(team_id):
    players = Player.objects.filter(team=team_id)
    for player in players:
        print(player)

def print_player_points(team_id):
    players = Player.objects.filter(team=team_id)
    for player in players:
        print(player.name, player.points)

def update_points(team_id, points_table):
    players = Player.objects.filter(team=team_id)
    for index, player in enumerate(players):
        player.points = points_table[index]
        player.save()

def update_score():
    squads = Squad.objects.all()
    for squad in squads:
        user = User.objects.get(id=squad.user_id)
        user_stat = UserStat.objects.get(user=user.id)
        user.score = user_stat.total_score + squad.compute_score()
        user.save()

def print_user_score():
    users = User.objects.all()
    for user in users:
        print(user.id, user.name, user.score)
