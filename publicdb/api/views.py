from django.contrib.auth import authenticate
from django.http import Http404

from rest_framework import permissions, views, status, viewsets, decorators
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.tokens import RefreshToken

import csv

from pdapp.models import Category, Dataset, DatasetFile
from .serializers import DatasetFileToJsonSerializer, CategorySerializer, DatasetSerializer, DatasetFileSerializer


class ObtainTokenView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        if username is None or password is None:
            return Response({"detail": "Username and password required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({"detail": "Invalid username/password."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.groups.filter(name='Editor').exists() and not user.is_superuser:
            return Response({"detail": "Access denied. You do not have permissions to generate a token."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class DatasetFileAjaxAPIView(views.APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def check_permissions(self, request):
        if request.method != 'POST':
            return
        return super().check_permissions(request)
    
    def get_object(self, pk):
        try:
            datasetfile = DatasetFile.objects.get(pk=pk)
            if not datasetfile.confirmed:
                return Http404
            return datasetfile
        
        except DatasetFile.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        datasetfile = self.get_object(pk)
        serializer = DatasetFileToJsonSerializer(datasetfile)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        datasetfile = self.get_object(pk)
        if not datasetfile.confirmed:
            return Response({'detail': 'Datasetfile not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        labels = request.data.get('labels', None)
        values = request.data.get('values', None)

        if labels is not None and values is not None:
            with open(datasetfile.file_csv.path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(labels)
                writer.writerow(values)

            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response({'detail': 'Labels and values required.'}, status=status.HTTP_400_BAD_REQUEST)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated]
        return super(CategoryViewSet, self).get_permissions()

    @decorators.action(detail=True, methods=['get'])
    def datasets(self, request, pk=None):
        category = self.get_object()
        datasets = Dataset.objects.filter(category=category)
        serializer = DatasetSerializer(datasets, many=True)
        return Response(serializer.data)


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'category__name']

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated]
        return super(DatasetViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id is not None:
            queryset = queryset.filter(category__id=category_id)
        return queryset

    @decorators.action(detail=True, methods=['get'])
    def datasetfiles(self, request, pk=None):
        dataset = self.get_object()
        datasetfiles = DatasetFile.objects.filter(dataset=dataset)
        serializer = DatasetFileSerializer(datasetfiles, many=True)
        return Response(serializer.data)


class DatasetFileViewSet(viewsets.ModelViewSet):
    queryset = DatasetFile.objects.all()
    serializer_class = DatasetFileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'dataset__name', 'provider', 'date_creation']

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated]
        return super(DatasetFileViewSet, self).get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        dataset_id = self.request.query_params.get('dataset_id')
        if dataset_id is not None:
            queryset = queryset.filter(dataset__id=dataset_id)
        return queryset
