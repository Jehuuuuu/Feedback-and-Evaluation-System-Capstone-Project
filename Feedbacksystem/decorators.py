from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.is_authenticated:
                if request.user.groups.exists:
                    group = request.user.groups.all()[0].name

                if group in allowed_roles:
                    return view_func(request, *args, **kwargs)
                
                else:
                    messages.error(request, 'You are not authorized to view this page.')
                    return redirect('signin')
            else: 
                messages.error(request, 'You must be logged in to access this page. Please login to continue.') 
                return redirect('signin')
                    
        return wrapper_func
    return decorator
