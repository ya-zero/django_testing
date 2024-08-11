# test_content.py
import pytest
from django.urls import reverse
from news.forms import CommentForm
from django.conf import settings


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
    ),
)
@pytest.mark.parametrize(
    # Задаём названия для параметров:
    'parametrized_client, form_in_list',
    (
        # Передаём фикстуры в параметры при помощи "ленивых фикстур":
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
@pytest.mark.django_db
def test_create_comment_page_contains_form(
    parametrized_client,
    form_in_list,
    name,
    args
):
    """
    Пункт 4 , Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости,а авторизованному доступна
    """
    url = reverse(name, args=args)
    # Запрашиваем страницу создания новости:
    response = parametrized_client.get(url)
    # Проверяем, есть ли объект form в словаре контекста:
    assert ('form' in response.context) == form_in_list
    if form_in_list:
        # Проверяем, что объект формы относится к нужному классу.
        assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_news_count_posts(client, more_news):
    """Пункт 1 Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE



# 2 Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка
@pytest.mark.django_db
def test_news_sort_posts(client, more_news):
    """Пункт 1 Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    sorted_news_list = sorted(object_list, key=lambda x: x.date, reverse=True)
    assert list(object_list) == sorted_news_list
