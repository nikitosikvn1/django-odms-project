from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.APIview.as_view(), name='categories'),
    path('categories/<int:pk>/', views.APIview_pk.as_view(), name='categories'),

    path('datasets/', views.APIview.as_view(), name='datasets'),
    path('datasets/<int:pk>/', views.APIview_pk.as_view(), name='datasets'),

    path('files/', views.APIview.as_view(), name='files'),
    path('files/<int:pk>/', views.APIview_pk.as_view(), name='files'),
]