from django.test import TestCase, RequestFactory, Client
from unittest.mock import Mock
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.contrib import auth
from django.contrib.messages import get_messages
from redis_sessions.session import SessionStore as RedisSessionStore

from django.contrib.auth.models import User, AnonymousUser, Group
from .models import Category, Dataset, DatasetFile
from .decorators import unauthenticated_user, allowed_users
from .forms import RegistrationForm, CustomAuthenticationForm
from .validators import validate_csv_file
from publicdb.settings import MEDIA_ROOT

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
import os
import csv

# Function to delete files created during tests
def delete_test_entries(starts_with: str) -> None:
    directory = f"{MEDIA_ROOT}/csv"
    if os.path.exists(directory):
        test_files = [f for f in os.listdir(directory) if f.startswith(starts_with)]
        for file in test_files:
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

# ------------------------------
# ----------> MODELS <----------
# ------------------------------
class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", hex_code="#FFFFFF")

    def test_string_representation(self):
        self.assertEqual(str(self.category), self.category.name)

    def test_verbose_name_plural(self):
        self.assertEqual(str(Category._meta.verbose_name_plural), "Categories")


class DatasetModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", hex_code="#FFFFFF")
        self.dataset = Dataset.objects.create(name="Test Dataset", description="Test description", category=self.category)

    def test_string_representation(self):
        self.assertEqual(str(self.dataset), f"{self.dataset.name} : {self.dataset.category}")

    def test_verbose_name_plural(self):
        self.assertEqual(str(Dataset._meta.verbose_name_plural), "Datasets")


class DatasetFileModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", hex_code="#FFFFFF")
        self.user = User.objects.create_user(username='testuser', password='TestPassword123')
        self.dataset = Dataset.objects.create(name="Test Dataset", description="Test description", category=self.category)
        file_content = b'meow meow meow'
        self.dataset_file = DatasetFile.objects.create(
            name="Test DatasetFile",
            description="Test description",
            dataset=self.dataset,
            created_by=self.user,
            provider="Test provider",
            file_csv=SimpleUploadedFile('testfile1.csv', file_content)
        )

    def test_string_representation(self):
        self.assertEqual(str(self.dataset_file), f"{self.dataset_file.name} : {self.dataset_file.created_by}")

    def test_verbose_name_plural(self):
        self.assertEqual(str(DatasetFile._meta.verbose_name_plural), "DatasetFiles")
    
    def test_validation_csv_file(self):
        file_content = b'it doesnt fucking matter'
        with self.assertRaises(ValidationError):
            dataset_file = DatasetFile(
                name="Validation error file",
                description="Another description",
                dataset=self.dataset,
                created_by=self.user,
                provider="IDK",
                file_csv=SimpleUploadedFile('testfile2.txt', file_content)
            )
            dataset_file.full_clean()
    
    def tearDown(self):
        delete_test_entries('test')


class DatasetModelRelationshipTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", hex_code="#FFFFFF")
        self.dataset = Dataset.objects.create(name="Test Dataset", description="Test description", category=self.category)

    def test_dataset_category_relationship(self):
        self.assertEqual(self.dataset.category, self.category)
    
    def test_category_deletion(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()


class DatasetFileModelRelationshipTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", hex_code="#FFFFFF")
        self.dataset = Dataset.objects.create(name="Test Dataset", description="Test description", category=self.category)
        self.user = User.objects.create_user(username='testuser', password='TestPassword123')
        file_content = b'meow meow meow'
        self.dataset_file = DatasetFile.objects.create(
            name="Test DatasetFile",
            description="Test description",
            dataset=self.dataset,
            created_by=self.user,
            provider="Test provider",
            file_csv=SimpleUploadedFile('testfile3.csv', file_content)
        )

    def test_datasetfile_dataset_relationship(self):
        self.assertEqual(self.dataset_file.dataset, self.dataset)
    
    def test_datasetfile_created_by_relationship(self):
        self.assertEqual(self.dataset_file.created_by, self.user)

    def test_dataset_deletion(self):
        self.dataset.delete()
        with self.assertRaises(DatasetFile.DoesNotExist):
            DatasetFile.objects.get(id=self.dataset_file.id)
    
    def test_user_deletion(self):
        with self.assertRaises(ProtectedError):
            self.user.delete()
    
    def tearDown(self):
        delete_test_entries('test')


# ------------------------------
# --------> DECORATORS <--------
# ------------------------------
class UnauthenticatedUserDecoratorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test', password='12345')

    def test_decorator_with_unauthenticated_user(self):

        @unauthenticated_user
        def mock_view(request):
            return 'Hello, world!'

        request = self.factory.get('/fake-path')
        request.user = AnonymousUser()
        response = mock_view(request)

        self.assertEqual(response, 'Hello, world!')

    def test_decorator_with_authenticated_user(self):

        @unauthenticated_user
        def mock_view(request):
            return 'Hello, world!'

        request = self.factory.get('/fake-path')
        request.user = self.user
        response = mock_view(request)

        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse('index'))


class AllowedUsersDecoratorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='test', password='12345')
        self.group1 = Group.objects.create(name='group1')
        self.group2 = Group.objects.create(name='group2')

    def test_decorator_with_allowed_group(self):

        @allowed_users(allowed_roles=['group1'])
        def mock_view(request):
            return HttpResponse('Hello, world!')

        self.group1.user_set.add(self.user)
        
        request = self.factory.get('/fake-path')
        request.user = self.user
        response = mock_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Hello, world!')

    def test_decorator_with_unallowed_group(self):

        @allowed_users(allowed_roles=['group1'])
        def mock_view(request):
            return HttpResponse('Hello, world!')

        self.group2.user_set.add(self.user)
        
        request = self.factory.get('/fake-path')
        request.user = self.user
        response = mock_view(request)

        self.assertEqual(response.status_code, 403)

    def test_decorator_with_no_group(self):

        @allowed_users(allowed_roles=['group1'])
        def mock_view(request):
            return HttpResponse('Hello, world!')

        request = self.factory.get('/fake-path')
        request.user = self.user
        response = mock_view(request)

        self.assertEqual(response.status_code, 403)


# ------------------------------
# --------> VALIDATORS <--------
# ------------------------------
class ValidateCSVFileTest(TestCase):
    def test_validate_csv_file_valid_extension(self):
        valid_file = SimpleUploadedFile("file.csv", b"file_content", content_type="text/csv")
        validate_csv_file(valid_file)

    def test_validate_csv_file_invalid_extension(self):
        invalid_file = SimpleUploadedFile("file.txt", b"file_content", content_type="text/plain")

        with self.assertRaises(ValidationError):
            validate_csv_file(invalid_file)


# ------------------------------
# --------> URL ROUTES <--------
# ------------------------------
class URLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.file = SimpleUploadedFile("testfile.csv", b"a,b\n1,2", content_type="text/csv")
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(name='TestCategory')
        self.dataset = Dataset.objects.create(name='TestDataset', description='TestDescription', category=self.category)
        self.datasetfile = DatasetFile.objects.create(
            name='TestFile',
            description='Test file description',
            file_csv=self.file,
            dataset=self.dataset,
            created_by=self.user,
            provider='TestProvider',
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_auth_view(self):
        response = self.client.get(reverse('auth'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_profile_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_dataset_view(self):
        response = self.client.get(reverse('dataset', kwargs={'pk': self.dataset.pk}))
        self.assertEqual(response.status_code, 200)

    def test_file_view(self):
        response = self.client.get(reverse('file', kwargs={'pk': self.datasetfile.pk}))
        self.assertEqual(response.status_code, 200)

    def test_faq_view(self):
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)

    def test_export_xlsx_view(self):
        response = self.client.get(reverse('exportXLSX', kwargs={'pk': self.datasetfile.pk}))
        self.assertEqual(response.status_code, 200)

    def test_export_csv_view(self):
        response = self.client.get(reverse('exportCSV', kwargs={'pk': self.datasetfile.pk}))
        self.assertEqual(response.status_code, 200)

    def test_export_plot_view(self):
        response = self.client.get(reverse('exportPlot', kwargs={'pk': self.datasetfile.pk}))
        self.assertEqual(response.status_code, 200)
    
    def tearDown(self):
        delete_test_entries('test')


# Integration test to check the interaction between Django and Redis.
# I didn't do any complex Redis setup, so the test is more of a demo.
class RedisSessionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_redis_session_on_login(self):
        response = self.client.post(reverse('auth'), {
            'username': 'testuser',
            'password': '12345',
            'login': '',
        })
        self.assertEqual(response.status_code, 302)

        session_key = self.client.session.session_key
        redis_session_store = RedisSessionStore(session_key=session_key)
        session_data = redis_session_store.load()

        self.assertTrue(session_data)
        self.assertEqual(session_data.get('_auth_user_id'), str(self.user.pk))
    
    def tearDown(self):
        session_key = self.client.session.session_key
        if session_key:
            redis_session_store = RedisSessionStore(session_key=session_key)
            redis_session_store.delete()


# ------------------------------
# ----------> VIEWS <-----------
# ------------------------------
class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        self.categories = [
            Category.objects.create(name=f"Category {i}", hex_code="#ffffff")
            for i in range(6)
        ]

        self.datasets = [
            Dataset.objects.create(
                name=f"Dataset {i}", 
                description=f"Description for Dataset {i}", 
                category=self.categories[i%5]
            ) for i in range(20)
        ]

    def test_get_categories(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["categories"], Category.objects.all().order_by('id')[:5], transform=lambda x: x)

    def test_get_datasets_with_search(self):
        response = self.client.get(reverse("index"), {"search": "1"})
        header_context = response.context["header"]
        datasets_context = response.context["latestdatasets"]

        expected_queryset = Dataset.objects.filter(Q(name__icontains='1') | Q(description__icontains='1'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(header_context, "Search results for: '1'")
        self.assertEqual(len(datasets_context), min(10, len(expected_queryset)))
        self.assertQuerysetEqual(datasets_context, expected_queryset[:10], transform=lambda x: x)

    def test_get_datasets_with_search_second_page(self):
        response = self.client.get(reverse("index"), {"search": "1", "page": "2"})
        datasets_context = response.context["latestdatasets"]

        expected_queryset = Dataset.objects.filter(Q(name__icontains='1') | Q(description__icontains='1'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(datasets_context), min(10, max(0, len(expected_queryset) - 10)))
        self.assertQuerysetEqual(datasets_context, expected_queryset[10:20], transform=lambda x: x)

    def test_get_datasets_without_search(self):
        response = self.client.get(reverse("index"))
        header_context = response.context["header"]
        datasets_context = response.context["latestdatasets"]

        expected_queryset = Dataset.objects.all().order_by('-id')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(header_context, "Recent questions")
        self.assertEqual(len(datasets_context), min(10, len(expected_queryset)))
        self.assertQuerysetEqual(datasets_context, expected_queryset[:10], transform=lambda x: x)

    def test_no_datasets(self):
        Dataset.objects.all().delete()

        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["latestdatasets"]), 0)


class RegistrationAndLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.data = {
            'register': True,
            'username': 'testuser2',
            'email': 'testuser@example.com',
            'password1': 'Qatar1221!',
            'password2': 'Qatar1221!',
        }

    def test_get_request(self):
        response = self.client.get(reverse('auth'))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['registration_form'], RegistrationForm)
        self.assertIsInstance(response.context['login_form'], CustomAuthenticationForm)

    def test_register_post_request(self):
        response = self.client.post(reverse('auth'), data=self.data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=self.data['username']).exists())
        self.assertEqual(response.url, reverse('index'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully registered and logged in.")

    def test_invalid_register_post_request(self):
        invalid_data = self.data.copy()
        invalid_data['password2'] = 'differentpassword'
        response = self.client.post(reverse('auth'), data=invalid_data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data['username']).exists())
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Please correct the errors in the registration form.")

    def test_login_post_request(self):
        login_data = {
            'login': True,
            'username': 'testuser',
            'password': '12345'
        }
        
        response = self.client.post(reverse('auth'), data=login_data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully logged in.")

    def test_invalid_login_post_request(self):
        login_data = {
            'login': True,
            'username': 'testuser',
            'password': 'wrongpassword'
        }

        response = self.client.post(reverse('auth'), data=login_data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Invalid username or password.")
    
    def test_post_request_without_login_or_register(self):
        response = self.client.post(reverse('auth'), data={})
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 0)
        self.assertIsInstance(response.context['registration_form'], RegistrationForm)
        self.assertIsInstance(response.context['login_form'], CustomAuthenticationForm)
    
    # here we assume that registration takes precedence over login
    def test_register_and_login_post_request(self):
        self.data['login'] = True
        response = self.client.post(reverse('auth'), data=self.data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username=self.data['username']).exists())
        self.assertEqual(response.url, reverse('index'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully registered and logged in.")
        self.data.pop('login')
    
    def test_register_existing_user(self):
        existing_user_data = {
            'register': True,
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': '12345',
            'password2': '12345',
        }

        response = self.client.post(reverse('auth'), data=existing_user_data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Please correct the errors in the registration form.")
    
    def test_successful_login_authenticates_user(self):
        login_data = {
            'login': True,
            'username': 'testuser',
            'password': '12345'
        }

        _ = self.client.post(reverse('auth'), data=login_data)
        user = auth.get_user(self.client)

        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, login_data['username'])
    
    def test_unauthenticated_user_access(self):
        response = self.client.get(reverse('auth'))
        self.assertEqual(response.status_code, 200)
    
    def test_authenticated_user_access(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('auth'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('index'))


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_logout_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(response, reverse('auth'))
    
    def test_logout_view_unauthenticated_user(self):
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('auth'))


class DatasetViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.category = Category.objects.create(name="Test category", hex_code="#FFFFFF")
        cls.dataset = Dataset.objects.create(
            name="Test Dataset",
            description="Test description",
            category=cls.category,
        )

    def test_dataset_view_success_status_code(self):
        url = reverse('dataset', kwargs={'pk': self.dataset.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_dataset_view_not_found_status_code(self):
        url = reverse('dataset', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_dataset_in_context(self):
        url = reverse('dataset', kwargs={'pk': self.dataset.id})
        response = self.client.get(url)
        self.assertTrue('datasetinf' in response.context)
        self.assertEqual(response.context['datasetinf'], self.dataset)


class ExportXLSXViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_file_name = "test.csv"
        with open(self.test_file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Job", "Description"])
        self.test_file = open(self.test_file_name, 'rb')
        self.user = User.objects.create(username="Testuser", password="12345")
        self.category = Category.objects.create(name="Test Category", hex_code="#FFFFFF")
        self.dataset = Dataset.objects.create(
            name="Test dataset",
            description="Random description here",
            category=self.category,
        )
        self.dataset_file = DatasetFile.objects.create(
            name="Test", 
            description="Test description",
            file_csv=SimpleUploadedFile(self.test_file.name, self.test_file.read()),
            dataset=self.dataset,
            created_by=self.user,
            provider="Test provider", 
        )
        self.test_file.close()
        os.remove(self.test_file_name)
    
    def test_invalid_pk(self):
        response = self.client.get(f'/exportfile/xlsx/{self.dataset_file.id}abc/')
        self.assertEqual(response.status_code, 404)
    
    def test_nonexistent_dataset_file(self):
        response = self.client.get(f'/exportfile/xlsx/{self.dataset_file.id + 1}/')
        self.assertEqual(response.status_code, 404)
    
    def test_existing_dataset_file_with_content(self):
        response = self.client.get(f'/exportfile/xlsx/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    def test_existing_dataset_file_no_content(self):
        self.dataset_file.file_csv.delete()
        self.test_file_name = "test_empty.csv"
        with open(self.test_file_name, 'w', newline='') as file:
            pass
        self.test_file = open(self.test_file_name, 'rb')
        self.dataset_file.file_csv = SimpleUploadedFile(self.test_file.name, self.test_file.read())
        self.dataset_file.save()
        self.test_file.close()
        response = self.client.get(f'/exportfile/xlsx/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 500)
        os.remove(self.test_file_name)
    
    def test_existing_dataset_file_without_actual_csv_file(self):
        os.remove(self.dataset_file.file_csv.path)

        response = self.client.get(f'/exportfile/xlsx/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 500)
    
    def tearDown(self):
        delete_test_entries('test')
    

class ExportCSVViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_file_name = "test.csv"
        with open(self.test_file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Test1", "Test2", "Test3"])
        self.test_file = open(self.test_file_name, 'rb')
        self.user = User.objects.create(username="Testuser", password="12345")
        self.category = Category.objects.create(name="Test Category", hex_code="#FFFFFF")
        self.dataset = Dataset.objects.create(
            name="Test dataset",
            description="Random description here",
            category=self.category,
        )
        self.dataset_file = DatasetFile.objects.create(
            name="Test", 
            description="Test description",
            file_csv=SimpleUploadedFile(self.test_file.name, self.test_file.read()),
            dataset=self.dataset,
            created_by=self.user,
            provider="Test provider", 
        )
        self.test_file.close()
        os.remove(self.test_file_name)
    
    def test_valid_dataset_file(self):
        response = self.client.get(f'/exportfile/csv/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Info:,Test,Test description,Test provider' in response.content)
    
    def test_invalid_dataset_file_id(self):
        response = self.client.get('/exportfile/csv/abc/')
        self.assertEqual(response.status_code, 404)
    
    def test_nonexistent_dataset_file(self):
        response = self.client.get(f'/exportfile/csv/{self.dataset_file.id + 1}/')
        self.assertEqual(response.status_code, 404)
    
    def test_existing_dataset_file_empty_content(self):
        self.dataset_file.file_csv.delete()
        self.test_file_name = "test_empty.csv"
        with open(self.test_file_name, 'w', newline='') as file:
            pass
        self.test_file = open(self.test_file_name, 'rb')
        self.dataset_file.file_csv = SimpleUploadedFile(self.test_file.name, self.test_file.read())
        self.dataset_file.save()
        self.test_file.close()
        response = self.client.get(f'/exportfile/csv/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 500)
        os.remove(self.test_file_name)
    
    def test_existing_dataset_file_no_actual_file(self):
        os.remove(self.dataset_file.file_csv.path)
        response = self.client.get(f'/exportfile/csv/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 500)
    
    def tearDown(self):
        delete_test_entries('test')
    

class ExportPlotViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_file_name = "test.csv"
        with open(self.test_file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Label1", "Label2", "Label3"])
            writer.writerow([1.0, 2.0, 3.0])
        self.test_file = open(self.test_file_name, 'rb')
        self.user = User.objects.create(username="Testuser", password="12345")
        self.category = Category.objects.create(name="Test Category", hex_code="#FFFFFF")
        self.dataset = Dataset.objects.create(
            name="Test dataset",
            description="Random description here",
            category=self.category,
        )
        self.dataset_file = DatasetFile.objects.create(
            name="Test", 
            description="Test description",
            file_csv=SimpleUploadedFile(self.test_file.name, self.test_file.read()),
            dataset=self.dataset,
            created_by=self.user,
            provider="Test provider", 
        )
        self.test_file.close()
        os.remove(self.test_file_name)
    
    def test_valid_dataset_file(self):
        response = self.client.get(f'/exportfile/plot/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        
    def test_invalid_dataset_file_id(self):
        response = self.client.get('/exportfile/plot/abc/')
        self.assertEqual(response.status_code, 404)
    
    def test_nonexistent_dataset_file(self):
        response = self.client.get(f'/exportfile/plot/{self.dataset_file.id + 1}/')
        self.assertEqual(response.status_code, 404)
    
    def test_existing_dataset_file_empty_content(self):
        self.dataset_file.file_csv.delete()
        self.test_file_name = "test_empty.csv"
        with open(self.test_file_name, 'w', newline='') as file:
            pass
        self.test_file = open(self.test_file_name, 'rb')
        self.dataset_file.file_csv = SimpleUploadedFile(self.test_file.name, self.test_file.read())
        self.dataset_file.save()
        self.test_file.close()
        response = self.client.get(f'/exportfile/plot/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 404)
        os.remove(self.test_file_name)
    
    def test_existing_dataset_file_invalid_content(self):
        self.dataset_file.file_csv.delete()
        self.test_file_name = "test_invalid.csv"
        with open(self.test_file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Label1", "Label2", "Label3"])
            writer.writerow(["Invalid", "Data", "Here"])
        self.test_file = open(self.test_file_name, 'rb')
        self.dataset_file.file_csv = SimpleUploadedFile(self.test_file.name, self.test_file.read())
        self.dataset_file.save()
        self.test_file.close()
        response = self.client.get(f'/exportfile/plot/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 404)
        os.remove(self.test_file_name)
    
    def test_existing_dataset_file_no_actual_file(self):
        os.remove(self.dataset_file.file_csv.path)
        response = self.client.get(f'/exportfile/plot/{self.dataset_file.id}/')
        self.assertEqual(response.status_code, 404)
    
    def tearDown(self):
        delete_test_entries('test')