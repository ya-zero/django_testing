# test_routes.py
import pytest
from http import HTTPStatus
from django.urls import reverse
from news.models import News
from pytest_django.asserts import assertContains
from pytest_django.asserts import assertRedirects

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


# 3,5 Страницы удаления и редактирования комментария доступны автору комментария.
# проверим что она не достпна для не автора

# Добавляем к тесту ещё один декоратор parametrize; в его параметры
# нужно передать фикстуры-клиенты и ожидаемый код ответа для каждого клиента.
@pytest.mark.parametrize(
    # parametrized_client - название параметра, 
    # в который будут передаваться фикстуры;
    # Параметр expected_status - ожидаемый статус ответа.
    'parametrized_client, expected_status',
    # Предварительно оборачиваем имена фикстур 
    # в вызов функции pytest.lazy_fixture().
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)

@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:edit', 'news:delete')
    )
@pytest.mark.django_db
# В параметры теста добавляем имена parametrized_client и expected_status.
def test_comment_availability_for_auth_user(parametrized_client, expected_status, name, comment):
    # Получаем ссылку на нужный адрес.
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)  # Выполняем запрос.
    assert response.status_code == expected_status


# 4 При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.

@pytest.mark.parametrize(
    # Вторым параметром передаём note_object, 
    # в котором будет либо фикстура с объектом заметки, либо None.
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_args')),
        ('news:delete', pytest.lazy_fixture('pk_for_args')),

    ),
)
@pytest.mark.django_db
# Передаём в тест анонимный клиент, name проверяемых страниц и note_object:
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
