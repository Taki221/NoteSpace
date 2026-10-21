from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('notes/', views.notes_view, name='notes'),

    path('api/login/', views.api_login, name='api_login'),
    path('api/notes/', views.api_notes, name='api_notes'),
    path('api/notes/<int:pk>/', views.api_note_detail, name='api_note_detail'),

]