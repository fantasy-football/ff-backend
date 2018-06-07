from django.middleware.csrf import get_token

def set_cookies(view_func):
    def new_view_func(request):
        decorated_func = view_func(request)
        if 'csrftoken' not in request.COOKIES:
            decorated_func.set_cookie('csrftoken', get_token(request), 2592000)
        return decorated_func
    return new_view_func
