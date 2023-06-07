from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
     path('api-token-auth/', views.ObtainTokenView.as_view(), name='api-token-auth'),
     path('api-token-refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),
]