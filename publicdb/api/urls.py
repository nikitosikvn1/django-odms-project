from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'datasets', views.DatasetViewSet, basename='dataset')
router.register(r'datasetfiles', views.DatasetFileViewSet, basename='datasetfile')

urlpatterns = [
     path('', include(router.urls)),
     path('api-token-auth/', views.ObtainTokenView.as_view(), name='api-token-auth'),
     path('api-token-refresh/', TokenRefreshView.as_view(), name='api-token-refresh'),

     path('datasetfile-data/<int:pk>/', views.DatasetFileAjaxAPIView.as_view(), name='datasetfile-data'),
]