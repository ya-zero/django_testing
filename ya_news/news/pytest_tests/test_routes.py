# test_routes.py
import pytest
from http import HTTPStatus
from django.urls import reverse
from news.models import News
from pytest_django.asserts import assertContains


# Пункты 1,6
# Главная страница доступна анонимному пользователю.
# Страницы регистрации пользователей, входа в учётную запись и выхода
# из неё доступны анонимным пользователям. +
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
@pytest.mark.django_db
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# 2 Страница отдельной новости доступна анонимному пользователю.
@pytest.mark.django_db
def test_pages_detal_availability_for_anonymous_user(client, news):
    # Получаем ссылку на нужный адрес.
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


# 3 Страницы удаления и редактирования комментария доступны автору комментария.
# проверим что она не достпна для не автора 
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:edit', 'news:delete')
    )
@pytest.mark.django_db
def test_comment_availability_for_auth_user(parametrized_client, expected_status, name, comment):
    # Получаем ссылку на нужный адрес.
    # print('comment id: %s author:%s' % (comment.pk, comment.author))
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)  # Выполняем запрос.
    assert response.status_code == expected_status

