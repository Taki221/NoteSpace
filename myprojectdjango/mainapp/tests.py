import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .forms import TaskForm
from .models import Task


User = get_user_model()


class TaskModelTests(TestCase):
    # Проверки полей заметки и значений, заданных моделью по умолчанию.

    def test_task_has_expected_defaults_and_string_representation(self):
        # Новая заметка создаётся с ожидаемыми флагами и названием в __str__.
        task = Task.objects.create(title='Моя заметка', content='Текст')

        self.assertEqual(str(task), 'Моя заметка')
        self.assertFalse(task.is_favorite)
        self.assertFalse(task.is_deleted)
        self.assertIsNone(task.user)
        self.assertIsNotNone(task.created_at)
        self.assertIsNone(task.updated_at)


class TaskFormTests(TestCase):
    # Проверки полей формы и валидации до записи данных в базу.

    def test_form_accepts_valid_data(self):
        # Корректные название и содержимое проходят валидацию.
        form = TaskForm(data={
            'title': 'Новая заметка',
            'content': 'Текст заметки',
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['title'], 'Новая заметка')
        self.assertEqual(form.cleaned_data['content'], 'Текст заметки')

    def test_form_requires_title(self):
        # Название обязательно, даже если содержимое заметки задано.
        form = TaskForm(data={'title': '', 'content': 'Текст заметки'})

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_accepts_empty_content(self):
        # Модель разрешает пустое содержимое заметки.
        form = TaskForm(data={'title': 'Заметка без текста', 'content': ''})

        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_whitespace_only_title(self):
        # Пробелы вместо названия не должны приниматься как полезные данные.
        form = TaskForm(data={
            'title': '   ',
            'content': 'Текст заметки',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_rejects_title_longer_than_model_limit(self):
        # Форма не принимает название длиннее ограничения модели в 100 символов.
        form = TaskForm(data={
            'title': 'А' * 101,
            'content': 'Текст заметки',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_only_exposes_title_and_content(self):
        # Через форму нельзя передать владельца, id или служебные поля модели.
        self.assertEqual(list(TaskForm().fields), ['title', 'content'])


class PageViewTests(TestCase):
    # Проверки страниц, формы входа и отображения пользовательских данных.

    def setUp(self):
        # Создаём двух пользователей для проверки изоляции их заметок.
        self.user = User.objects.create_user(
            username='first-user',
            password='correct-test-password',
        )
        self.other_user = User.objects.create_user(
            username='second-user',
            password='other-test-password',
        )

    def test_index_page_opens_for_anonymous_user(self):
        # Главная страница доступна без входа и предлагает авторизацию.
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/index.html')
        self.assertContains(response, reverse('login'))
        self.assertEqual(list(response.context['tasks']), [])

    def test_index_only_provides_current_users_notes(self):
        # В контексте главной страницы есть только заметки текущего пользователя.
        own_task = Task.objects.create(title='Моя заметка', user=self.user)
        Task.objects.create(title='Чужая заметка', user=self.other_user)
        self.client.force_login(self.user)

        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['tasks']), [own_task])

    def test_notes_page_renders(self):
        # Страница заметок возвращает соответствующий шаблон.
        response = self.client.get(reverse('notes'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/notes.html')

    def test_login_page_renders(self):
        # Страница входа доступна и содержит форму аутентификации.
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/login.html')
        self.assertIn('form', response.context)

    def test_valid_login_authenticates_user(self):
        # Верные учётные данные создают сессию и перенаправляют на главную.
        response = self.client.post(reverse('login'), {
            'username': 'first-user',
            'password': 'correct-test-password',
        })

        self.assertRedirects(response, reverse('index'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_login_keeps_user_anonymous(self):
        # Неверный пароль не авторизует пользователя и повторно показывает форму.
        response = self.client.post(reverse('login'), {
            'username': 'first-user',
            'password': 'wrong-test-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/login.html')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_authenticated_user_is_redirected_from_login_page(self):
        # Авторизованному пользователю повторно открывать страницу входа незачем.
        self.client.force_login(self.user)

        response = self.client.get(reverse('login'))

        self.assertRedirects(response, reverse('index'))

    def test_logout_clears_authentication_and_redirects_to_login(self):
        # Выход завершает сессию и возвращает пользователя к форме входа.
        self.client.force_login(self.user)

        response = self.client.get(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class ApiLoginTests(TestCase):
    # Проверки входа через JSON API.

    def setUp(self):
        # Создаём пользователя с паролем, который можно использовать в запросе.
        self.user = User.objects.create_user(
            username='api-user',
            password='correct-api-password',
        )

    def post_json(self, url, data):
        # Отправляем JSON в формате, который использует клиентское приложение.
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )

    def test_api_login_authenticates_user_with_valid_credentials(self):
        # Успешный вход возвращает статус ok и авторизует последующие запросы.
        response = self.post_json(reverse('api_login'), {
            'username': 'api-user',
            'password': 'correct-api-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        notes_response = self.client.get(reverse('api_notes'))
        self.assertEqual(notes_response.status_code, 200)

    def test_api_login_rejects_invalid_json(self):
        # Некорректное тело JSON отклоняется с понятным кодом ошибки.
        response = self.client.post(
            reverse('api_login'),
            data='{',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_api_login_requires_username_and_password(self):
        # Отсутствие логина или пароля не позволяет создать сессию.
        for data in ({'username': 'api-user'}, {'password': 'secret'}):
            with self.subTest(data=data):
                response = self.post_json(reverse('api_login'), data)

                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.json())

    def test_api_login_rejects_incorrect_credentials(self):
        # Неверный пароль отклоняется и не авторизует клиента.
        response = self.post_json(reverse('api_login'), {
            'username': 'api-user',
            'password': 'wrong-api-password',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        self.assertEqual(
            self.client.get(reverse('api_notes')).status_code,
            401,
        )


class NotesApiTests(TestCase):
    # Проверки создания, получения, изменения и удаления заметок через API.

    def setUp(self):
        # Подготавливаем владельца заметок и отдельного пользователя.
        self.user = User.objects.create_user(
            username='notes-owner',
            password='owner-test-password',
        )
        self.other_user = User.objects.create_user(
            username='other-owner',
            password='other-owner-password',
        )
        self.client.force_login(self.user)

    def post_json(self, url, data):
        # Отправляем JSON в формате API заметок.
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )

    def put_json(self, url, data):
        # Отправляем частичное или полное обновление заметки как JSON.
        return self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json',
        )

    def test_notes_api_requires_authentication(self):
        # Все методы API заметок требуют входа даже для известных id.
        self.client.logout()
        responses = (
            self.client.get(reverse('api_notes')),
            self.client.post(
                reverse('api_notes'),
                data='{}',
                content_type='application/json',
            ),
            self.client.put(
                reverse('api_note_detail', args=[999]),
                data='{}',
                content_type='application/json',
            ),
            self.client.delete(reverse('api_note_detail', args=[999])),
        )

        for response in responses:
            with self.subTest(status=response.status_code):
                self.assertEqual(response.status_code, 401)
                self.assertIn('error', response.json())

    def test_get_notes_returns_only_current_users_notes_in_updated_order(self):
        # Список содержит только заметки пользователя и сортируется по обновлению.
        older_task = Task.objects.create(
            title='Старая',
            user=self.user,
            updated_at=timezone.now() - timedelta(days=1),
        )
        newer_task = Task.objects.create(
            title='Новая',
            user=self.user,
            updated_at=timezone.now(),
        )
        Task.objects.create(title='Чужая', user=self.other_user)

        response = self.client.get(reverse('api_notes'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [note['id'] for note in response.json()],
            [newer_task.id, older_task.id],
        )
        self.assertEqual(
            [note['title'] for note in response.json()],
            ['Новая', 'Старая'],
        )

    def test_create_note_saves_content_and_uses_authenticated_user(self):
        # Созданная заметка принадлежит текущему пользователю и сохраняет текст.
        response = self.post_json(reverse('api_notes'), {
            'title': '  Новая заметка  ',
            'content': 'Текст заметки',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        task = Task.objects.get(pk=response.json()['id'])
        self.assertEqual(task.title, 'Новая заметка')
        self.assertEqual(task.content, 'Текст заметки')
        self.assertEqual(task.user, self.user)
        self.assertFalse(task.is_favorite)
        self.assertFalse(task.is_deleted)

    def test_create_note_uses_default_title_when_title_is_blank(self):
        # Пустое название заменяется стандартной подписью без потери содержимого.
        response = self.post_json(reverse('api_notes'), {
            'title': '   ',
            'content': 'Текст без названия',
        })

        self.assertEqual(response.status_code, 200)
        task = Task.objects.get(pk=response.json()['id'])
        self.assertEqual(task.title, 'Без названия')
        self.assertEqual(task.content, 'Текст без названия')

    def test_create_note_rejects_invalid_json(self):
        # Некорректный JSON не создаёт запись в базе данных.
        response = self.client.post(
            reverse('api_notes'),
            data='{',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Task.objects.count(), 0)

    def test_create_note_rejects_title_longer_than_model_limit(self):
        # Название длиннее 100 символов отклоняется до сохранения.
        response = self.post_json(reverse('api_notes'), {
            'title': 'А' * 101,
            'content': 'Текст',
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Task.objects.count(), 0)

    def test_update_note_changes_allowed_fields_and_timestamp(self):
        # PUT обновляет поля заметки и фиксирует время изменения.
        old_updated_at = timezone.now() - timedelta(days=1)
        task = Task.objects.create(
            title='Старое название',
            content='Старый текст',
            user=self.user,
            updated_at=old_updated_at,
        )

        response = self.put_json(
            reverse('api_note_detail', args=[task.pk]),
            {
                'title': 'Новое название',
                'content': 'Новый текст',
                'is_favorite': True,
                'is_deleted': True,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        task.refresh_from_db()
        self.assertEqual(task.title, 'Новое название')
        self.assertEqual(task.content, 'Новый текст')
        self.assertTrue(task.is_favorite)
        self.assertTrue(task.is_deleted)
        self.assertGreater(task.updated_at, old_updated_at)

    def test_update_note_uses_default_title_when_title_is_blank(self):
        # Пустое название при изменении заменяется стандартной подписью.
        task = Task.objects.create(title='Старое название', user=self.user)

        response = self.put_json(
            reverse('api_note_detail', args=[task.pk]),
            {'title': '   '},
        )

        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Без названия')

    def test_update_note_rejects_invalid_json_without_changing_note(self):
        # Некорректное тело PUT не изменяет существующую заметку.
        task = Task.objects.create(
            title='Исходное название',
            content='Исходный текст',
            user=self.user,
        )

        response = self.client.put(
            reverse('api_note_detail', args=[task.pk]),
            data='{',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Исходное название')
        self.assertEqual(task.content, 'Исходный текст')

    def test_update_note_rejects_title_longer_than_model_limit(self):
        # Слишком длинное название отклоняется без изменения существующей записи.
        task = Task.objects.create(title='Исходное название', user=self.user)

        response = self.put_json(
            reverse('api_note_detail', args=[task.pk]),
            {'title': 'А' * 101},
        )

        self.assertEqual(response.status_code, 400)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Исходное название')

    def test_update_and_delete_cannot_access_another_users_note(self):
        # Редактирование и удаление чужой заметки возвращают 404 и не меняют её.
        task = Task.objects.create(
            title='Чужая заметка',
            user=self.other_user,
        )
        url = reverse('api_note_detail', args=[task.pk])

        update_response = self.put_json(url, {'title': 'Подмена'})
        delete_response = self.client.delete(url)

        self.assertEqual(update_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        task.refresh_from_db()
        self.assertEqual(task.title, 'Чужая заметка')

    def test_update_and_delete_return_404_for_unknown_note(self):
        # Несуществующий id не приводит к созданию или изменению заметки.
        url = reverse('api_note_detail', args=[999])

        update_response = self.put_json(url, {'title': 'Название'})
        delete_response = self.client.delete(url)

        self.assertEqual(update_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.assertEqual(Task.objects.count(), 0)

    def test_delete_permanently_removes_only_requested_note(self):
        # DELETE удаляет выбранную запись, не затрагивая другие заметки владельца.
        task_to_delete = Task.objects.create(
            title='Удалить',
            user=self.user,
        )
        task_to_keep = Task.objects.create(
            title='Оставить',
            user=self.user,
        )

        response = self.client.delete(
            reverse('api_note_detail', args=[task_to_delete.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertFalse(Task.objects.filter(pk=task_to_delete.pk).exists())
        self.assertTrue(Task.objects.filter(pk=task_to_keep.pk).exists())

# Первый запуск из папки myprojectdjango: создай окружение и установи зависимости:
# py -m venv .venv
# .\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Запуск Django-тестов из папки myprojectdjango:
# .\.venv\Scripts\python.exe manage.py test mainapp
