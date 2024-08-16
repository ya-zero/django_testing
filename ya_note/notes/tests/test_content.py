# notes/tests/test_content.py
# Импортируем функцию для определения модели пользователя.
from django.contrib.auth import get_user_model
from django.test import TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse
from notes.forms import NoteForm
# Импортируем класс Заметок.
from notes.models import Note

# Получаем модель пользователя.
User = get_user_model()


class TestContent(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.no_author = User.objects.create(username='Не Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            slug='zagolovok',
            author=cls.author,
            text='Текст комментария'
        )
        cls.note_no_author = Note.objects.create(
            title='Заголовок',
            slug='zagolovok_',
            author=cls.no_author,
            text='Текст комментария'
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_object_list(self):
        """
        Отдельная заметка передаётся на страницу со
        списком заметок в списке object_list в словаре context;
        """
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_object_list_another_user(self):
        """
        В список заметок одного пользователя не попадают
        заметки другого пользователя
        """
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertNotIn(self.note_no_author, object_list)

    def test_authorized_client_has_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                response = self.client.get(reverse(name, args=args))
                self.assertIn('form', response.context)
                # Проверим, что объект формы соответствует классу формы.
                self.assertIsInstance(response.context['form'], NoteForm)
