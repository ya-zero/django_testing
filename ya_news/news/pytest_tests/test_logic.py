import pytest
from django.urls import reverse
from news.models import News, Comment
from pytest_django.asserts import assertRedirects

@pytest.mark.django_db
def test_anonymous_user_cant_create_note(client,news, form_data):
    """Пункт1 Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:edit', args=(news.pk,))
    # Через анонимный клиент пытаемся создать заметку:
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    # Проверяем, что произошла переадресация на страницу логина:
    assertRedirects(response, expected_url)
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 0

