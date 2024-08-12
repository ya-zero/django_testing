# test_content.py
import pytest
from django.urls import reverse
from news.forms import CommentForm
from django.conf import settings
from news.models import News, Comment
from django.utils import timezone
from datetime import timedelta


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


@pytest.mark.django_db
def test_news_sort(client):
    """
    Пукт 2 Новости отсортированы от самой свежей к
    самой старой. Свежие новости в начале списка
    """
    # Создаем тестовые новости с разными датами, если нет fixture more_news
    older_news = News.objects.create(
        title='Old News',
        text='Old News Text',
        date=timezone.now() - timedelta(days=2)
    )
    newer_news = News.objects.create(
        title='New News',
        text='New News Text',
        date=timezone.now()
    )
    response = client.get(reverse('news:home'))
    news_titles = [news.title for news in response.context['object_list']]
    assert news_titles[0] == newer_news.title  # Новый должен быть первым
    assert news_titles[1] == older_news.title   # Старый должен быть вторым


@pytest.mark.django_db
def test_comment_sort(client, author, news):
    """
    #Пункт 3 Комментарии на странице отдельной новости отсортированы в
    # хронологическом порядке: старые в начале списка, новые — в конце.
    """
    older_coment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст 0',
        created=timezone.now() - timedelta(days=2)
    )
    newer_coment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст 1',
        created=timezone.now())
    response = client.get(reverse('news:detail', args=(news.pk,)))
    comment_titles = [
        comment.text for comment in response.context["news"].comment_set.all()
    ]
    assert comment_titles[0] == older_coment.text   # Старый должен быть первым
    assert comment_titles[1] == newer_coment.text  # Новый должен быть вторым
