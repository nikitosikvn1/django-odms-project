from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('auth/', views.RegistrationAndLoginView.as_view(), name='auth'),
    # path('registration/', views.RegistrationView.as_view(), name='registration'),
    # path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('dataset/<int:pk>/', views.DatasetView.as_view(), name='dataset'),
    path('file/<int:pk>/', views.FileChartView.as_view(), name='file'),
    # INFO
    path('info/faq/', views.FaqView.as_view(), name='faq'),
    # EXPORT
    path('exportfile/xlsx/<int:pk>/', views.ExportXLSXView.as_view(), name='exportXLSX'),
    path('exportfile/csv/<int:pk>/', views.ExportCSVView.as_view(), name='exportCSV'),
    path('exportfile/plot/<int:pk>/', views.ExportPlotView.as_view(), name='exportPlot'),
    # API
    path('api/tabledata/<int:pk>/', views.TableDataAPIView.as_view(), name='tabledata')
]