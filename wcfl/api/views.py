from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Player, Fixture, Squad
from common.models import User

import json


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
                             'teamId': player.team.id
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


def submit_squad(request):
    if request.method == 'POST':
        
        try:
            user_id = request.session.get('user')
            user = User.objects.get(id = user_id)

        except Exception as e:
            print(e)
            return JsonResponse({'Error': 'User not logged in'}, status=403)

        data = json.loads(request.body.decode('utf-8'))
         
        starting_list = []
        substitute_list = []
        
        squad = []

        captain_id = data['captain']['id']
        vc_id = data['vc']['id']

        for player in data['squad']:
            squad.append(player['id'])

        for substitute in data['subs']:
            substitute_list.append(substitute['id'])
            
        starting_list = list(set(squad)-(set(substitute_list).union(set([captain_id, vc_id]))))

        sq = Squad.create(user_id, starting_list, substitute_list, captain_id, vc_id)
        print(sq.starting.all(), sq.substitutes.all())

        return JsonResponse({'Succes': True})
    else:
        return JsonResponse({'Error': 'Invalid request'}, status=405)



def get_lineup(request):
    
    if request.method == 'GET':

        try:
            user_id = request.session.get('user')
            user = User.objects.get(id = user_id)

            if user.squad_created == False:
                return JsonResponse({'Error': 'Squad not yet created'}, status=403)

            squad = Squad.objects.get(user = user_id)

            data = squad.get_data()
            return JsonResponse({'data': data})

        except Exception as e:
            return JsonResponse({'Error': 'Something bad happened'}, status=500)

    else:
        return JsonResponse({'Error': 'Invalid request'}, status=405)
