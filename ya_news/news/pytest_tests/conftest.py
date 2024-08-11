# conftest.py
import pytest

# Импортируем класс клиента.
from django.test.client import Client

# Импортируем модель новости, чтобы создать экземпляр.
from news.models import News, Comment
from django.conf import settings


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    post = News.objects.create(  # Создаём объект новости.
        title='Заголовок',
        text='Текст новости',
    )
    return post


@pytest.fixture
def more_news(db):
    for _ in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(  # Создаём объект новости.
            title='Заголовок',
            text='Текст новости',
        )


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(news=news, author=author, text='Текст')


@pytest.fixture
# Фикстура запрашивает другую фикстуру создания новости.
def pk_for_args(comment):
    # И возвращает кортеж, который содержит id новости.
    # На то, что это кортеж, указывает запятая в конце выражения.
    return (comment.pk,)
