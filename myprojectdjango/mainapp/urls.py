from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete/<int:pk>/', views.delete_task, name='delete_task'), #URL который принимает запросы на удаление конкретной задачи
    path('edit/<int:pk>/', views.edit_task, name='edit_task'), #URL редактирования
]