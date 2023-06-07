from django.contrib.auth import authenticate
from django.http import Http404

from rest_framework import permissions, views, generics, status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

import csv

from pdapp.models import Category, Dataset, DatasetFile
from .serializers import DatasetFileToJsonSerializer


class ObtainTokenView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        if username is None or password is None:
            return Response({"detail": "Username and password required."}, status=400)

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({"detail": "Invalid username/password."}, status=400)

        if not user.groups.filter(name='Editor').exists():
            return Response({"detail": "Access denied. You do not have permissions to generate a token."}, status=403)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class DatasetFileAjaxAPIView(views.APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
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
