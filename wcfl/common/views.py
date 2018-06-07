from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import User
from .decorators import set_cookies

import requests
import json


@csrf_exempt
def sign_in(request):
    if request.method == "POST":

        data = json.loads(request.body.decode('utf-8'))

        if 'access_token' in data:
            access_token = data['access_token']
        else:
            return JsonResponse({'Error': 'User not authorized'},
                                status=401)

        try:
            headers = {'Authorization': 'Bearer % s' % access_token}
            r = requests.get('https://wcfl.auth0.com/userinfo',
                             headers=headers)

            userinfo = r.json()
            userinfo['sub'] = userinfo['sub'].split('|')[1]

            if not User.objects.filter(id=userinfo['sub']).exists():
                obj = User.objects.create(id=userinfo['sub'],
                                          name=userinfo['name'],
                                          profile_picture=userinfo['picture'],
                                          email=userinfo['email'])
            else:
                obj = User.objects.get(id=userinfo['sub'])

            request.session['user'] = obj.id
            request.session['logged_in'] = True

            return JsonResponse({'success': True})

        except Exception as e:
            print('Unable to fetch userinfo', e)
            return JsonResponse({'Error': 'Authorization failed'},
                                status=500)

    else:
        return JsonResponse({'Error': 'Method not allowed'}, status=405)


@set_cookies
def set_token(request):
    if request.method == "GET":
        return JsonResponse({'Success': True})
    else:
        return JsonResponse({'Error': 'Invalid Request'}, status=405)


def sign_out(request):
    if request.method == "GET":
        request.session.flush()
        return JsonResponse({'Success': True})
    else:
        return JsonResponse({'Error': 'Invalid Request'}, status=405)
