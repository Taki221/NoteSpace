from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm

# Create your views here.
def index(request): #ГЛАВНАЯ ФУНКЦИЯ СТРАНИЦЫ

    if request.method == 'POST':
        form = TaskForm(request.POST) #Заполняем форму
        if form.is_valid(): #Встроенная проверка верности заполнения
            form.save() #Сохраняем в бд
            return redirect('/')
    else:
        form = TaskForm #Пустая форма если get запрос



    #ДОСТАВАНИЕ ДАННЫХ ИЗ БД
    tasks = Task.objects.all()


    #ПЕРЕМЕННЫЕ ПРИ РЕНДЕРЕ ИНДЕКСА
    context = {
        'username': 'Taki',
        'tasks': tasks,
        'form': form,
    }

    return render(request, 'mainapp/index.html', context)

def delete_task(request, pk): #ФУНКЦИЯ УДАЛЕНИЯ
    task = get_object_or_404(Task, pk=pk) #Поиск по ID
    task.delete()
    return redirect('index')

def edit_task(request, pk): #ФУНКЦИЯ РЕДАКТИРОВАНИЯ
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = TaskForm(instance=task) #передаём instance=task чтобы форма сразу была заполнена текущими данными

    return render(request, 'mainapp/index.html', {'form': form, 'tasl': task})