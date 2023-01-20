from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.urls import resolve

from pdapp.models import Category, Dataset, DatasetFile
from .serializers import CategorySerializer, DatasetSerializer, DatasetFileSerializer


data = {
    'categories': {
        'model': Category,
        'serializer': CategorySerializer
    },
    'datasets': {
        'model': Dataset,
        'serializer': DatasetSerializer
    },
    'files': {
        'model': DatasetFile,
        'serializer': DatasetFileSerializer
    }
}


# GET LIST, POST
class APIview(generics.ListCreateAPIView):
    def get_queryset(self):
        URLname = resolve(self.request.path_info).url_name
        Model = data[URLname]['model']
        return Model.objects.all()

    def get_serializer_class(self):
        URLname = resolve(self.request.path_info).url_name
        return data[URLname]['serializer']


# GET BY ID, PUT, DELETE
class APIview_pk(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        URLname = resolve(self.request.path_info).url_name
        Model = data[URLname]['model']
        return Model.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=self.kwargs['pk'])
        return obj

    def get_serializer_class(self):
        URLname = resolve(self.request.path_info).url_name
        return data[URLname]['serializer']