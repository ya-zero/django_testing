import pytest
from django.urls import reverse
from news.models import News, Comment
from pytest_django.asserts import assertRedirects
from news.forms import BAD_WORDS, WARNING


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

@pytest.mark.django_db
def test_user_cant_comment_bad_words(author_client,news):
    """
    Пункт 2 Если комментарий содержит запрещённые слова, он не будет опубликован, а форма вернёт ошибку.
    """
    form_data={'text': f'Привет {BAD_WORDS[0]}',}
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=form_data)
    # print(response.context['form'].errors.keys())
    # raise ValidationError(WARNING) return text
    assert WARNING in response.context['form'].errors['text']
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_auth_user_send_comment(author_client,news,author):
    """
    Пункт 3 Авторизованный пользователь может отправить комментарий.
    """
    form_data={'text': f'Привет я {author}',}
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=form_data)
    # raise ValidationError(WARNING) return text
    #assert WARNING in response.context['form'].errors['text']
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 1
    assert Comment.objects.get().author == author
    assert Comment.objects.get().text == form_data['text']

