from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('auth/', views.RegistrationAndLoginView.as_view(), name='auth'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('dataset/<int:pk>/', views.DatasetView.as_view(), name='dataset'),
    path('file/<int:pk>/', views.FileChartView.as_view(), name='file'),
    path('file/<int:pk>/edit/', views.EditDatasetFileView.as_view(), name='editfile'),

    # INFO
    path('info/faq/', views.FaqView.as_view(), name='faq'),

    # EXPORT
    path('exportfile/xlsx/<int:pk>/', views.ExportXLSXView.as_view(), name='exportXLSX'),
    path('exportfile/csv/<int:pk>/', views.ExportCSVView.as_view(), name='exportCSV'),
    path('exportfile/plot/<int:pk>/', views.ExportPlotView.as_view(), name='exportPlot'),
]