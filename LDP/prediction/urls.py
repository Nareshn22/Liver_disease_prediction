

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('predict/', views.predict, name='predict'),
    path('download/<int:prediction_id>/', views.download_report, name='download_report'),
]







