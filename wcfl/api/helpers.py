from .models import Team, Player, Squad, PlayerStat
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


def reset_all_points():
    players = Player.objects.all()
    for player in players:
        Player.reset_points(player.id)


def update_score():
    squads = Squad.objects.all()
    for squad in squads:
        user = User.objects.get(id=squad.user_id)
        user_stat, created = UserStat.objects.get_or_create(user=user)
        user.score = user_stat.total_score + squad.compute_score()
        user.save()


def print_user_score():
    users = User.objects.all()
    for user in users:
        print(user.id, user.name, user.score)


def r16(qualified_teams):
    for team_id in qualified_teams:
        team = Team.objects.get(id=team_id)
        team.prequarter_finalist = True
        team.save()


def print_r16():
    teams = Team.objects.all()
    for team in teams:
        if team.prequarter_finalist:
            print(team.id, team.name)


def update_player_value():
    players = Player.objects.all()
    for player in players:
        if player.team.prequarter_finalist:
            player_stat = PlayerStat.objects.get(player=player)
            
            if player.value >= 10:
                
                if player_stat.total_points >= 25:
                    player.value += 1.5
                
                elif player_stat.total_points >= 20:
                    player.value += 1 
                
                elif player_stat.total_points >= 15:
                    player.value += 0.5

                elif player_stat.total_points >= 10:
                    player.value -= 0.5

                elif player_stat.total_points >= 5:
                    player.value -= 1

                else: 
                    player.value -= 2
            
            elif player.value >= 7:
 
                if player_stat.total_points >= 25:
                    player.value += 2.5
                
                elif player_stat.total_points >= 20:
                    player.value += 2
                
                elif player_stat.total_points >= 15:
                    player.value += 1.5

                elif player_stat.total_points >= 10:
                    player.value += 1

                elif player_stat.total_points >= 8:
                    player.value += 0.5

                elif player_stat.total_points >= 5:
                    player.value -= 0.5

                else: 
                    player.value -= 1

            else:
 
                if player_stat.total_points >= 25:
                    player.value += 4
                
                elif player_stat.total_points >= 20:
                    player.value += 3 
                
                elif player_stat.total_points >= 15:
                    player.value += 2

                elif player_stat.total_points >= 10:
                    player.value += 1.5

                elif player_stat.total_points >= 5:
                    player.value += 1

                elif player_stat.total_points >= 3: 
                    player.value += 0.5

                else:
                    player.value -= 0.5
           
            player.save()


def print_r16_players():
    players = Player.objects.all()
    for player in players:
        if player.team.prequarter_finalist:
            print(player.id, player.name, player.value)


def update_balance():
    users = User.objects.all()
    for user in users:
        if user.squad_created:
            balance = Squad.compute_value(user)
            user.balance = balance
            user.save()


def reset_all_squads():
    users = User.objects.all()
    for user in users:
        User.reset_squad(user.id)
