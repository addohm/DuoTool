from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.enteruser, name='enteruser'),
    path('success/', views.success, name='success'),
    path('<str:username>/', views.home, name='home'),
]
