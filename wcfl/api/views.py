from django.http import JsonResponse
from .models import Player, Fixture


def players_list(request):
    if request.method == "GET":
        try:
            players = Player.objects.all()
            data = []

            for player in players:
                data.append({'id': player.id, 'name': player.name,
                             'position': player.position,
                             'value': player.value,
                             'points': player.points,
                             'trigram': player.team.trigram,
                             'teamId': player.team.teamId
                             })

            return JsonResponse({'data': data})

        except Exception as e:
            # To be changed during deployment.
            print(e)
            return JsonResponse({'Error': 'Could not fetch players'},
                                 status=500)

    else:
        return JsonResponse({'Error': 'Invalid request'}, status=405)


def fixtures_list(request):
    if request.method == "GET":
        try:
            fixtures = Fixture.objects.all()
            data = []

            for fixture in fixtures:
                data.append({'id': fixtures.id, 'team1': fixtures.team1.name,
                             'team2': fixtures.team2.name,
                             'score1': fixtures.score1,
                             'score2': fixtures.score2,
                             'time': fixture.gametime,
                             'completed': fixture.completed
                             })

                return JsonResponse({'data': data})

        except Exception as e:
            print(e)
            return JsonResponse({'Error': 'Could not fetch fixtures'},
                                status=500)

    else:
        return JsonResponse({'Error': 'Invalid request'}, status=405)
