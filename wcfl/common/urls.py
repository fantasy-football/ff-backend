from django.urls import path

from .views import sign_in, sign_out, set_token, get_user_details, get_ranklist

urlpatterns = [
        path('signin', sign_in, name='sign_in'),
        path('signout', sign_out, name='sign_out'),
        path('token', set_token, name='set_token'),
        path('userinfo', get_user_details, name='get_user_details'),
        path('ranklist', get_ranklist, name='get_ranklist')
        ]
