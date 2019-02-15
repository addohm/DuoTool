from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    # path('', views.home),
    path('success/', views.success, name='success'),
    path('<str:username>/', views.home, name='home'),
    path('test/<str:username>/', views.test, name='test'),
]
