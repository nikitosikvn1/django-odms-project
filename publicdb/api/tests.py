import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.test import Client, TestCase
from mixer.backend.django import mixer

from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from pdapp.models import Category, Dataset, DatasetFile
from pdapp.tests import delete_test_entries

from .serializers import (
    CategorySerializer,
    DatasetSerializer,
    DatasetFileSerializer,
    DatasetFileToJsonSerializer,
)


# ------------------------------
# --------> Serializers <-------
# ------------------------------
class CategorySerializerTestCase(TestCase):
    def test_serializer_returns_expected_data(self):
        category = Category.objects.create(name='Test Category', hex_code='#FFFFFF')
        serializer = CategorySerializer(instance=category)
        expected_data = {
            'id': category.id,
            'name': 'Test Category',
            'hex_code': '#FFFFFF',
        }
        self.assertEqual(serializer.data, expected_data)


class DatasetSerializerTestCase(TestCase):
    def test_serializer_returns_expected_data(self):
        category = Category.objects.create(name='Test Category', hex_code='#FFFFFF')
        dataset = Dataset.objects.create(name='Test Dataset', description='Test', category=category)
        serializer = DatasetSerializer(instance=dataset)
        expected_data = {
            'id': dataset.id,
            'name': 'Test Dataset',
            'description': 'Test',
            'category': CategorySerializer(category).data.get('id'),
        }
        self.assertEqual(serializer.data, expected_data)


class DatasetFileSerializerTestCase(TestCase):
    def test_serializer_returns_expected_data(self):
        user = User.objects.create(username='Testuser', password='12345')
        category = Category.objects.create(name='Test Category', hex_code='#FFFFFF')
        dataset = Dataset.objects.create(name='Test Dataset', description='Test', category=category)
        dataset_file = DatasetFile.objects.create(
            name='Test File',
            description='Test',
            file_csv=SimpleUploadedFile('test.csv', b'csv_content'),
            dataset=dataset,
            created_by=user,
            provider='Test Provider',
            date_creation='2023-01-01',
            confirmed=True,
        )
        serializer = DatasetFileSerializer(instance=dataset_file)
        expected_data = {
            'id': dataset_file.id,
            'name': 'Test File',
            'description': 'Test',
            'file_csv': dataset_file.file_csv.url,
            'dataset': DatasetSerializer(dataset).data.get('id'),
            'created_by': user.id,
            'provider': 'Test Provider',
            'date_creation': '2023-01-01',
            'confirmed': True,
        }
        self.assertEqual(serializer.data, expected_data)
    
    def tearDown(self):
        delete_test_entries('file')


class DatasetFileToJsonSerializerTestCase(TestCase):
    def test_get_labels_returns_expected_data(self):
        user = User.objects.create(username='Testuser', password='12345')
        category = Category.objects.create(name='Test Category', hex_code='#FFFFFF')
        dataset = Dataset.objects.create(name='Test Dataset', description='Test', category=category)
        dataset_file = DatasetFile.objects.create(
            name='Test File',
            description='Test',
            file_csv=SimpleUploadedFile('test.csv', b'label1,label2,label3\n12,24,40'),
            dataset=dataset,
            created_by=user,
            provider='Test Provider',
            date_creation='2023-01-01',
            confirmed=True,
        )
        serializer = DatasetFileToJsonSerializer()

        labels = serializer.get_labels(dataset_file)
        values = serializer.get_values(dataset_file)

        expected_labels = ['label1', 'label2', 'label3']
        expected_values = ['12', '24', '40']

        self.assertEqual(labels, expected_labels)
        self.assertEqual(values, expected_values)

    def tearDown(self):
        delete_test_entries('file')


# ------------------------------
# ---------> API Views <--------
# ------------------------------
class ObtainTokenViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.editor_group = Group.objects.create(name='Editor')

    def test_token_generation_with_valid_credentials(self):
        user = User.objects.create_user(username='testuser', password='testpassword')
        user.groups.add(self.editor_group)

        url = reverse('api-token-auth')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

        refresh_token = RefreshToken(response.data['refresh'])

        self.assertEqual(str(refresh_token), response.data['refresh'])

    def test_token_generation_with_invalid_credentials(self):
        url = reverse('api-token-auth')
        data = {'username': 'invaliduser', 'password': 'invalidpassword'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'detail': 'Invalid username/password.'})

    def test_token_generation_without_credentials(self):
        url = reverse('api-token-auth')
        data = {}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'detail': 'Username and password required.'})

    def test_token_generation_without_editor_group(self):
        user = User.objects.create_user(username='testuser', password='testpassword')

        url = reverse('api-token-auth')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': 'Access denied. You do not have permissions to generate a token.'})
    

class DatasetFileAjaxAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345')
        self.user.save()
        self.datasetfile = mixer.blend(DatasetFile, confirmed=True)
        self.url = reverse('datasetfile-data', kwargs={'pk': self.datasetfile.pk})
    
    def test_get_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_get_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_nonexistent_datasetfile(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('datasetfile-data', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_get_unconfirmed_datasetfile(self):
        unconfirmed_datasetfile = mixer.blend(DatasetFile, confirmed=False)
        url = f'/datasetfile-data/{unconfirmed_datasetfile.pk}'
        self.client.login(username='testuser', password='12345')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_post_authenticated(self):
        self.client.login(username='testuser', password='12345')
        labels = ['label1', 'label2']
        values = ['value1', 'value2']
        response = self.client.post(self.url, {'labels': labels, 'values': values})
        self.assertEqual(response.status_code, 204)
    
    def test_post_unauthenticated(self):
        labels = ['label1', 'label2']
        values = ['value1', 'value2']
        response = self.client.post(self.url, {'labels': labels, 'values': values})
        self.assertEqual(response.status_code, 403)
    
    def test_post_nonexistent_datasetfile(self):
        self.client.login(username='testuser', password='12345')
        url = '/datasetfile-data/999999'
        labels = ['label1', 'label2']
        values = ['value1', 'value2']
        response = self.client.post(url, {'labels': labels, 'values': values})
        self.assertEqual(response.status_code, 404)
    
    def test_post_unconfirmed_datasetfile(self):
        unconfirmed_datasetfile = mixer.blend(DatasetFile, confirmed=False)
        url = f'/datasetfile-data/{unconfirmed_datasetfile.pk}'
        self.client.login(username='testuser', password='12345')
        labels = ['label1', 'label2']
        values = ['value1', 'value2']
        response = self.client.post(url, {'labels': labels, 'values': values})
        self.assertEqual(response.status_code, 404)
    
    def test_post_missing_labels_and_values(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)
    
    def tearDown(self):
        delete_test_entries('file')
