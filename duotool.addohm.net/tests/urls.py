from django.urls import path

from . import views

app_name = 'tests'

urlpatterns = [
    path('duolingo/', views.duolingo_test, name='duotest'),
    path('hsk/', views.hsk_select, name='hskselect'),
    path('hsk/<int:level>/', views.hsk_test, name='hsktest'),
]
