from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail

from django.views.generic import View, TemplateView, DetailView, UpdateView, FormView
from django.contrib.auth.views import LogoutView as AuthLogoutView

from .forms import RegistrationForm, CustomAuthenticationForm, DatasetFileUploadForm, UserUpdateForm
from .mixins import UserIsOwnerMixin, UnauthenticatedUserMixin, UserHasRoleMixin
from .decorators import unauthenticated_user, allowed_users
from .models import Category, Dataset, DatasetFile, EmailConfirmation

import csv
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from openpyxl import Workbook

# Create your views here.

class IndexView(TemplateView):
    template_name = "pdapp/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("search")
        latestdatasets, header = self.get_datasets(search_query)

        context['categories'] = self.get_categories()
        context['latestdatasets'] = latestdatasets
        context['header'] = header
        return context

    def get_datasets(self, search_query):
        datasets = Dataset.objects.select_related('category')

        if search_query:
            datasets = datasets.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )
            header = f"Search results for: '{search_query}'"
        else:
            datasets = datasets.order_by('-id')
            header = "Recent questions"

        paginator = Paginator(datasets, 10)
        page_number = self.request.GET.get('page')
        datasets = paginator.get_page(page_number)

        return datasets, header

    def get_categories(self):
        return Category.objects.all()[:5]
    

class RegistrationAndLoginView(UnauthenticatedUserMixin, View):

    def get(self, request):
        registration_form = RegistrationForm()
        login_form = CustomAuthenticationForm()

        return render(request, "pdapp/registration_and_login.html", {
            'registration_form': registration_form,
            'login_form': login_form,
        })
    
    def post(self, request):
        if 'register' in request.POST:
            registration_form = RegistrationForm(request.POST)
            login_form = CustomAuthenticationForm()

            if registration_form.is_valid():
                with transaction.atomic():
                    user = registration_form.save(commit=False)
                    user.is_active = False
                    user.save()

                    email_confirmation = EmailConfirmation.objects.create(user=user, email=user.email)
                    email_confirmation.send_confirmation_mail()

                    messages.success(request, "Please confirm your email address to complete the registration.")
                    return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, 'Please correct the errors in the registration form.')
        else:
            registration_form = RegistrationForm()
        
        if 'login' in request.POST:
            login_form = CustomAuthenticationForm(data=request.POST)
            registration_form = RegistrationForm()

            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                messages.success(request, "Successfully logged in.")
                return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            login_form = CustomAuthenticationForm()
        
        return render(request, "pdapp/registration_and_login.html", {
            'registration_form': registration_form,
            'login_form': login_form,
        })


class ConfirmEmailView(DetailView):
    model = EmailConfirmation
    slug_field = 'confirmation_key'
    slug_url_kwarg = 'uuid'

    def get(self, request, *args, **kwargs):
        confirmation = self.get_object()

        if confirmation.is_expired:
            confirmation.generate_new_confirmation()
            return HttpResponse("Confirmation link expired. We have sent a new confirmation link to your email.")

        user = confirmation.user
        user.is_active = True
        user.save()
        confirmation.delete()

        return HttpResponse("Email confirmed successfully. You can now log in.")


class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('auth')


class DatasetView(DetailView):
    model = Dataset
    template_name = "pdapp/dataset.html"
    context_object_name = "datasetinf"


class FileChartView(DetailView):
    model = DatasetFile
    template_name = "pdapp/filechart.html"
    context_object_name = "datasetfile"


class EditDatasetFileView(UserHasRoleMixin, TemplateView):
    allowed_roles = ['Editor']
    template_name = "pdapp/editdatasetfile.html"


class FaqView(TemplateView):
    template_name = "pdapp/faq.html"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'pdapp/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        password = form.cleaned_data.get('confirm_password')
        
        if self.request.user.check_password(password):
            return super().form_valid(form)
        else:
            messages.error(self.request, "Incorrect password. Please try again.")
            return super().form_invalid(form)


# EXPORT VIEWS

class ExportXLSXView(View):
    def get(self, request, pk):
        try:
            pk = int(pk)
        except ValueError:
            raise Http404("Invalid dataset file ID")

        obj = get_object_or_404(DatasetFile, pk=pk)
        path = obj.file_csv.path

        wb = Workbook()
        ws = wb.active
        ws.append(['Info:', obj.name, obj.description, obj.provider])

        try:
            with open(path, newline='') as csvfile:
                content = list(csv.reader(csvfile))

                if not content:
                    raise ValueError("The CSV file is empty")

                for row in content:
                    ws.append(row)
        except Exception as e:
            return HttpResponse(f"Error processing the file: {e}", status=500)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={obj.name}.xlsx'

        try:
            wb.save(response)
        except Exception as e:
            return HttpResponse(f"Error saving the file: {e}", status=500)

        return response


class ExportCSVView(View):
    def get(self, request, pk):
        try:
            pk = int(pk)
        except ValueError:
            raise Http404("Invalid dataset file ID")

        obj = get_object_or_404(DatasetFile, pk=pk)
        path = obj.file_csv.path

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{obj.name}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Info:', obj.name, obj.description, obj.provider])

        try:
            with open(path, newline='') as csvfile:
                content = list(csv.reader(csvfile))

                if not content:
                    raise ValueError("The CSV file is empty")

                for row in content:
                    writer.writerow(row)
        except Exception as e:
            return HttpResponse(f"Error processing the file: {e}", status=500)

        return response


class ExportPlotView(View):
    def get(self, request, pk):
        obj = get_object_or_404(DatasetFile, pk=pk)
        path = obj.file_csv.path

        try:
            with open(path, 'r') as f:
                reader = csv.reader(f)
                labels = next(reader)
                values = next(reader)

            if not labels or not values:
                raise ValueError('Empty labels or values')

            values = [float(val) for val in values]
        except Exception as e:
            raise Http404('Cannot read data from file: ' + str(e))

        sns.set_theme(style="darkgrid")
        fig, ax = plt.subplots()
        ax.plot(labels, values)
        ax.set_title(f"{obj.name} Plot", fontsize=14, fontweight='bold')
        ax.set_xlabel('Labels', fontsize=12)
        ax.set_ylabel('Values', fontsize=12)
        plt.xticks(rotation=45, fontsize=3) 

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        plt.close(fig)

        response = HttpResponse(buf.getvalue(), content_type='image/png')
        return response
    