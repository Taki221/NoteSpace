from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Task
from .forms import TaskForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'mainapp/login.html', {'form': form})

def notes_view(request):
    return render(request, 'mainapp/notes.html') 

def index(request):
    tasks = Task.objects.filter(user=request.user) if request.user.is_authenticated else []
    form = TaskForm()
    return render(request, 'mainapp/index.html', {'tasks': tasks, 'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)

        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'error': 'Введите логин и пароль'}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'error': 'Неверный логин или пароль'}, status=400)

def check_auth(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)
    return None

@csrf_exempt
def api_notes(request):
    auth_error = check_auth(request)
    if auth_error: return auth_error

    if request.method == 'GET':
        notes = list(Task.objects.filter(user=request.user).order_by('-updated_at').values())
        return JsonResponse(notes, safe=False)
        
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат'}, status=400)

        title = data.get('title', '').strip()
        content = data.get('content', '')

        if not title:
            title = 'Без названия'
        if len(title) > 100:
            return JsonResponse({'error': 'Слишком длинное название (макс 100 символов)'}, status=400)

        new_note = Task.objects.create(
            title=title,
            content=content,
            user=request.user
        )
        return JsonResponse({'id': new_note.id, 'status': 'ok'})

@csrf_exempt
def api_note_detail(request, pk):
    auth_error = check_auth(request)
    if auth_error: return auth_error

    try:
        note = Task.objects.get(pk=pk, user=request.user)
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Заметка не найдена'}, status=404)
        
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат'}, status=400)

        if 'title' in data:
            title = data.get('title', '').strip()
            if len(title) > 100:
                return JsonResponse({'error': 'Слишком длинное название'}, status=400)
            note.title = title if title else 'Без названия'
            
        if 'content' in data:
            note.content = data.get('content')
            
        if 'is_favorite' in data:
            note.is_favorite = data.get('is_favorite')
            
        if 'is_deleted' in data:
            note.is_deleted = data.get('is_deleted')
            
        note.updated_at = timezone.now()
        note.save()
        return JsonResponse({'status': 'ok'})
        
    elif request.method == 'DELETE':
        note.delete()
        return JsonResponse({'status': 'ok'})