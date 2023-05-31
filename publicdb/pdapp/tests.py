from django.test import TestCase, RequestFactory
from unittest.mock import Mock
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth.models import User, AnonymousUser, Group
from .models import Category, Dataset, DatasetFile
from .decorators import unauthenticated_user, allowed_users

from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

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


# ------------------------------
# --------> DECORATORS <--------
# ------------------------------
class UnauthenticatedUserDecoratorTests(TestCase):
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


class AllowedUsersDecoratorTests(TestCase):
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