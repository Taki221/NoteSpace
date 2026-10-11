from django.test import Client, TestCase
from django.urls import reverse

from .forms import TaskForm
from .models import Task


class TaskFormTests(TestCase):
    # Проверки полей формы и валидации до записи данных в базу.

    def test_form_accepts_valid_data(self):
        # Корректные название и описание проходят валидацию.
        form = TaskForm(data={
            'title': 'Новая задача',
            'description': 'Описание задачи',
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['title'], 'Новая задача')
        self.assertEqual(form.cleaned_data['description'], 'Описание задачи')

    def test_form_requires_title_and_description(self):
        # Отсутствие любого обязательного поля делает форму невалидной.
        invalid_data = (
            {'title': '', 'description': 'Описание задачи'},
            {'title': 'Новая задача', 'description': ''},
        )

        for data in invalid_data:
            with self.subTest(data=data):
                form = TaskForm(data=data)

                self.assertFalse(form.is_valid())
                self.assertTrue(form.errors)

    def test_form_rejects_whitespace_only_title(self):
        # Пробелы вместо названия не должны приниматься как полезные данные.
        form = TaskForm(data={
            'title': '   ',
            'description': 'Описание задачи',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_rejects_title_longer_than_model_limit(self):
        # Форма не принимает название длиннее ограничения модели в 100 символов.
        form = TaskForm(data={
            'title': 'А' * 101,
            'description': 'Описание задачи',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_only_exposes_allowed_model_fields(self):
        # Через форму нельзя передать id или временные поля модели.
        self.assertEqual(list(TaskForm().fields), ['title', 'description'])

    def test_form_ignores_unlisted_input_fields(self):
        # Лишние POST-поля не попадают в очищенные данные формы.
        form = TaskForm(data={
            'title': 'Новая задача',
            'description': 'Описание задачи',
            'id': '999',
            'created_at': '2099-01-01',
            'unexpected': 'лишнее значение',
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            set(form.cleaned_data),
            {'title', 'description'},
        )


class TaskViewTests(TestCase):
    # Проверки страниц и операций создания, изменения и удаления задач.

    def test_index_page_opens_and_displays_existing_task(self):
        # Главная страница доступна и показывает сохранённую задачу.
        task = Task.objects.create(
            title='Сохранённая задача',
            description='Описание',
        )

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/index.html')
        self.assertContains(response, task.title)
        self.assertContains(response, task.description)

    def test_valid_post_creates_exactly_one_task(self):
        # Валидная отправка создаёт одну запись и перенаправляет на главную.
        response = self.client.post(reverse('index'), {
            'title': 'Новая задача',
            'description': 'Описание задачи',
        })

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.get()
        self.assertEqual(task.title, 'Новая задача')
        self.assertEqual(task.description, 'Описание задачи')

    def test_invalid_post_does_not_write_to_database(self):
        # Невалидные данные возвращают форму с ошибками и не создают запись.
        invalid_data = (
            {'title': '', 'description': 'Описание задачи'},
            {'title': 'Новая задача', 'description': ''},
            {'title': 'А' * 101, 'description': 'Описание задачи'},
        )

        for data in invalid_data:
            with self.subTest(data=data):
                response = self.client.post(reverse('index'), data)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(Task.objects.count(), 0)

    def test_unlisted_post_fields_do_not_change_other_model_fields(self):
        # Проверяет, что лишние поля из запроса браузера, включая id и даты,
        # не подменяют значения, которые Django задаёт при создании задачи.
        response = self.client.post(reverse('index'), {
            'title': 'Обычная задача',
            'description': 'Описание',
            'id': '999',
            'created_at': '2099-01-01 00:00:00',
            'updated_at': '2099-01-01 00:00:00',
            'unexpected': 'лишние данные',
        })

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Task.objects.count(), 1)
        task = Task.objects.get()
        self.assertNotEqual(task.pk, 999)
        self.assertEqual(task.title, 'Обычная задача')
        self.assertEqual(task.description, 'Описание')
        self.assertNotEqual(task.created_at.year, 2099)
        self.assertNotEqual(task.updated_at.year, 2099)

    def test_sql_like_text_is_stored_as_plain_text(self):
        # SQL-подобная строка остаётся текстом и не меняет число записей.
        suspicious_title = "'; DROP TABLE mainapp_task; --"

        response = self.client.post(reverse('index'), {
            'title': suspicious_title,
            'description': 'Обычный текст',
        })

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, suspicious_title)

    def test_post_without_csrf_token_is_rejected_without_writing(self):
        # CSRF middleware отклоняет POST без токена до сохранения данных.
        client = Client(enforce_csrf_checks=True)

        response = client.post(reverse('index'), {
            'title': 'Не должна сохраниться',
            'description': 'Запрос без CSRF-токена',
        })

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Task.objects.count(), 0)

    def test_valid_edit_updates_existing_task(self):
        # Валидное редактирование меняет задачу, не создавая новую.
        task = Task.objects.create(title='Старое название', description='Старое')

        response = self.client.post(reverse('edit_task', args=[task.pk]), {
            'title': 'Новое название',
            'description': 'Новое описание',
        })

        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Task.objects.count(), 1)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Новое название')
        self.assertEqual(task.description, 'Новое описание')

    def test_invalid_edit_does_not_change_task(self):
        # Невалидное редактирование не портит сохранённую задачу.
        task = Task.objects.create(title='Исходное название', description='Исходное')

        response = self.client.post(reverse('edit_task', args=[task.pk]), {
            'title': '',
            'description': 'Изменённое описание',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.count(), 1)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Исходное название')
        self.assertEqual(task.description, 'Исходное')

    def test_delete_removes_only_the_requested_task(self):
        # Удаление одной задачи не затрагивает остальные записи.
        task_to_delete = Task.objects.create(title='Удалить', description='Задача')
        task_to_keep = Task.objects.create(title='Оставить', description='Задача')

        response = self.client.post(
            reverse('delete_task', args=[task_to_delete.pk])
        )

        self.assertRedirects(response, reverse('index'))
        self.assertFalse(Task.objects.filter(pk=task_to_delete.pk).exists())
        self.assertTrue(Task.objects.filter(pk=task_to_keep.pk).exists())
        self.assertEqual(Task.objects.count(), 1)

    def test_edit_and_delete_return_404_for_unknown_task(self):
        # Несуществующий id не приводит к изменению базы и возвращает 404.
        edit_response = self.client.post(
            reverse('edit_task', args=[999]),
            {'title': 'Название', 'description': 'Описание'},
        )
        delete_response = self.client.post(reverse('delete_task', args=[999]))

        self.assertEqual(edit_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.assertEqual(Task.objects.count(), 0)


#cd C:\Users\KK\Desktop\myprojectdjango\myprojectdjango\projectmain
#python manage.py test mainapp