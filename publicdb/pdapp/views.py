from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm

# Create your views here.

def index(request):
    return render(request, 'pdapp/layout.html')

def registration_view(request):
    form = RegistrationForm()

    return render(request, "pdapp/registration.html", {
        "form": form,
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        print(f"{username=}, {password=}")

    return render(request, 'pdapp/login.html')