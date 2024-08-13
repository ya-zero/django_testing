from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


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
    assert WARNING in response.context['form'].errors['text']
    # Считаем количество заметок в БД, ожидаем 0 заметок.
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_auth_user_send_comment(author_client,news,author,):
    """
    Пункт 3 Авторизованный пользователь может отправить комментарий.
    """
    form_data={'text': f'Привет я {author}',}
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1
    comment_from_db = Comment.objects.get()
    assert comment_from_db.text == form_data['text']
    assert comment_from_db.author == author
    assert comment_from_db.news == news


@pytest.mark.django_db
def test_auth_user_send_comment(author_client,news,comment,pk_for_args,author):
    """
    Пункт 4 Авторизованный пользователь может редактировать или удалять свои комментарии.
    """
    # Новый текст
    form_data={'text': f'Привет я {author}',}
    # Редактирование коментария
    url = reverse('news:edit', args=pk_for_args)
    # В POST-запросе на адрес редактирования заметки
    # отправляем form_data - новые значения для полей заметки   
    response = author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, reverse('news:detail', args=pk_for_args) + '#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news
    # Удаление коментария 
    response = author_client.post(reverse('news:delete', args=pk_for_args))
    assert response.status_code == HTTPStatus.FOUND
    #test_auth_user_send_comment <HttpResponseRedirect status_code=302, "text/html; charset=utf-8", url="/news/1/#comments">
    assertRedirects(response, reverse('news:detail',args=pk_for_args) + "#comments")
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_auth_user_send_comment(not_author_client,news,comment,pk_for_args,not_author):
    """
    Пункт 5 Авторизованный пользователь не может редактировать или удалять чужие комментарии
    """
    form_data={'text': f'Привет я {not_author}',}
    # Редактирование коментария
    url = reverse('news:edit', args=pk_for_args)
    response = not_author_client.post(url, data=form_data)
    # Проверяем, что страница не найдена:
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    response = not_author_client.post(reverse('news:delete', args=pk_for_args))
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
