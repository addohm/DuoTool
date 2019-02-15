from django.urls import path

from . import views

urlpatterns = [
    # path('', views.home),
    path('<str:username>/', views.home, name='home'),
    path('<str:username>/test/', views.test, name='test'),
]
