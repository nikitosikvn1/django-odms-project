from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm

# Create your views here.

def index(request):
    logged = False

    return render(request, "pdapp/index.html", {
        "logged": logged
    })


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


def logout_view(request):
    pass

def profile(request):
    return HttpResponse("<h2>Your profile will be here!</h2>")