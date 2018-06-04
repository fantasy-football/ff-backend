from django.http import JsonResponse
from urllib import request as rq

def sign_in(request):
    if request.method == "POST":
        
        if 'access_token in request.POST:
            acess_token = request.POST['access_token']
        else:
            return JsonResponse({'Error': 'User not logged in'}, status=404)
        
        try:
	    headers = { 'Authorization' : 'Bearer %s'%access_token }
	    req = rq.Request('https://wcfl.auth0.com/userinfo', headers=headers)
            data = json.loads(rq.urlopen(req).read().decode("utf-8"))

        except Exception as e:
            return JsonResponse({'Error': Failed to retrieve user info'}, status=404)

        if not User.objects.filter(user_id=data['sub']).exists():

