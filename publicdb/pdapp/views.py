from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm

# Create your views here.

def index(request):
    return render(request, "pdapp/index.html")


def registration_view(request):
    form = RegistrationForm()

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            user = authenticate(request, username=user.username, password=request.POST["password1"])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))

    return render(request, "pdapp/registration.html", {
        "form": form,
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "pdapp/login.html", {
                "message": "Invalid credentials."
            })

    return render(request, "pdapp/login.html")


def logout_view(request):
    logout(request)

    return render(request, "pdapp/login.html", {
        "message": "Logged out."
    })

def profile(request):
    return HttpResponse("<h2>Your profile will be here!</h2>")

# Temp

def faq(request):
    return render(request, "pdapp/faq.html")