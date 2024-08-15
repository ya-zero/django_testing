
# /tests/test_routes.py
from http import HTTPStatus

# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

# Импортируем класс комментария.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        # cls.news = News.objects.create(title='Заголовок', text='Текст')
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Автор')
        cls.notauthor = User.objects.create(username='Не Автор')
        # От имени одного пользователя создаём заметку:
        cls.note = Note.objects.create(
            title='Заголовок',
            slug='zagolovok',
            author=cls.author,
            text='Текст комментария'
        )

    def test_guest_pages_availability(self):
        """Главная страница доступна анонимному пользователю."""
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_auth_pages_availability(self):
        """Аутентифицированному пользователю доступна страница.

        со списком заметок notes/,
        страница успешного добавления заметки done/,
        страница добавления новой заметки add/.
        """
        urls = (
            ('notes:list', self.author),
            ('notes:add', self.author),
            ('notes:success', self.author),
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.client.force_login(args)
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
