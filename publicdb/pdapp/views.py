import csv
from openpyxl import Workbook

from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q

from django.views.generic import View, TemplateView, DetailView, RedirectView

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import RegistrationForm, DatasetFileUploadForm
from .decorators import unauthenticated_user, allowed_users
from .models import Category, Dataset, DatasetFile

# Create your views here.

class IndexView(TemplateView):
    template_name = "pdapp/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get("search")

        if search_query:
            latestdatasets = Dataset.objects.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))
            header = f"Search results for: '{search_query}'"
        else:
            latestdatasets = Dataset.objects.order_by('-id')[:10]
            header = "Recent questions"

        context['categories'] = Category.objects.all()[:5] 
        context['latestdatasets'] = latestdatasets
        context['header'] = header
        return context


@method_decorator(unauthenticated_user, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class RegistrationView(View):

    def get(self, request):
        form = RegistrationForm()
        return render(request, "pdapp/registration.html", {'form': form})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            user = authenticate(request, username=user.username, password=request.POST["password1"])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))

        return render(request, "pdapp/registration.html", {'form': form})


@method_decorator(unauthenticated_user, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):

    def get(self, request):
        return render(request, "pdapp/login.html")

    def post(self, request):
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

class LogoutView(RedirectView):
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


#@method_decorator(allowed_users(["Analyst"]), name='dispatch')
class DatasetView(DetailView):
    model = Dataset
    template_name = "pdapp/dataset.html"
    context_object_name = "datasetinf"


class FileChartView(View):
    def get(self, request, pk):
        datasetfile = get_object_or_404(DatasetFile, pk=pk)

        return render(request, "pdapp/filechart.html", {
            "datasetfile": datasetfile,
        })


class FaqView(TemplateView):
    template_name = "pdapp/faq.html"


class ProfileView(TemplateView):
    template_name = "pdapp/profile.html"

# EXPORT VIEW

class ExportXLSXView(View):
    def get(self, request, pk):
        obj = get_object_or_404(DatasetFile, pk=pk)
        path = obj.file_csv.path

        wb = Workbook()
        ws = wb.active
        ws.append(['Info:', obj.name, obj.description, obj.provider])

        with open(path, newline='') as csvfile:
            content = list(csv.reader(csvfile))

            for row in content:
                ws.append(row)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={obj.name}.xlsx'

        wb.save(response)
        return response


class ExportCSVView(View):
    def get(self, request, pk):
        obj = get_object_or_404(DatasetFile, pk=pk)
        path = obj.file_csv.path

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{obj.name}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Info:', obj.name, obj.description, obj.provider])

        with open(path, newline='') as csvfile:
            content = list(csv.reader(csvfile))

            for row in content:
                writer.writerow(row)
    
        return response
    
# API VIEWS

class TableDataAPIView(APIView):
    def get(self, request, pk, *args, **kwargs):
        obj = get_object_or_404(DatasetFile, pk=pk)
        path = obj.file_csv.path

        with open(path, newline='') as csvfile:
            content = list(csv.reader(csvfile))

            dataJson = {
                "labels": content[0],
                "values": content[1]
            }

        return Response(dataJson, status=status.HTTP_200_OK)