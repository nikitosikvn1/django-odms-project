from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.core.exceptions import PermissionDenied


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))
        return view_func(request, *args, **kwargs)
    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            
            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                #raise PermissionDenied
                return render(request, "pdapp/HTTP403.html")
        return wrapper_func
    return decorator