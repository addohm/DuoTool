from django.urls import path

from . import views

urlpatterns = [
    path('', views.home),
    path('<username>/', views.home),
]
