# # ya_note/notes/tests/test_logic.py
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

# Получаем модель пользователя.
User = get_user_model()


class TestLogic(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.form_data = {
            'title': 'Заголовок_NEW',
            'slug': 'zagolovok_NEW',
            'text': 'Текст комментария'
        }
        cls.user = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

    def test_auth_user_cant_create_notes(self):
        """Залогиненный пользователь может создать заметку."""
        self.auth_client.post(reverse('notes:add'), data=self.form_data)
        # Считаем количество комментариев.
        current_count = Note.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(current_count, 1)

    def test_anonimous_user_cant_create_notes(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(reverse('notes:add'), data=self.form_data)
        # Считаем количество комментариев.
        current_count = Note.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(current_count, 0)

    def test_two_note_one_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.auth_client.post(reverse('notes:add'), data=self.form_data)
        response = self.auth_client.post(
            reverse('notes:add'),
            data=self.form_data
        )
        # можно проверить наличие сообщения при доабвлении второй записи
        self.assertIn(WARNING, response.context['form'].errors['slug'][0])
        # колличество записей
        self.assertEqual(Note.objects.count(), 1)

    def test_generate_slug_if_empty(self):
        """
        Если при создании заметки не заполнен slug,
        то он формируется автоматически, с помощью функции
        pytils.translit.slugify.
        """
        max_slug_length = Note._meta.get_field('slug').max_length
        self.auth_client.post(
            reverse('notes:add'),
            data={'title': 'Тестируем Slug', 'text': 'Текс заметки'}
        )
        self.assertEqual(
            Note.objects.get().slug,
            slugify(Note.objects.get().slug)[:max_slug_length]
        )


class TestLogicEdit(TestCase):
    NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'
    @classmethod
    def setUpTestData(cls):
        cls.form_data = {
            'title': 'Заголовок новый',
            'slug': 'zagolovoknew',
            'text': cls.NEW_NOTE_TEXT
        }
        cls.user = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            slug='zagolovok',
            author=cls.user,
            text=cls.NOTE_TEXT
        )
        cls.another_user = User.objects.create(username='Не Автор')
        cls.another_client = Client()
        cls.another_client.force_login(cls.another_user)

    def test_user_edit_notes(self):
        """Пользователь может редактировать"""
        response = self.auth_client.post(
           reverse('notes:edit', args=(self.note.slug,)),
           data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.form_data['text'])

    def test_user_delete_notes(self):
        """Пользователь может  удалять свои заметки"""
        response = self.auth_client.delete(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)
    # another user
    def test_another_user_edit_notes(self):
        """Пользователь не может редактировать чужие заметки"""
        response = self.another_client.post(
           reverse('notes:edit', args=(self.note.slug,)),
           data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Убедимся, что заметки по-прежнему на месте.
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_another_user_delete_notes(self):
        """Пользователь не может  удалять чужие заметки"""
        response = self.another_client.delete(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
