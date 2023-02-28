from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class TestUrl(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост про что то',
            group=cls.group
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(TestUrl.user)
        self.author_client = Client()
        self.author_client.force_login(TestUrl.author)

    def test_urls_available_to_everyone(self):
        """Проверка доступность для всех."""
        post_urls = {
            '/': HTTPStatus.OK,
            f'/group/{TestUrl.group.slug}/': HTTPStatus.OK,
            f'/profile/{TestUrl.user.username}/': HTTPStatus.OK,
            f'/posts/{TestUrl.post.pk}/': HTTPStatus.OK,
        }

        for url, result in post_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    result,
                )

    def test_404_page(self):
        """Проверка на 404 для несуществующей страницы."""
        response = self.guest_client.get('unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_availability_of_url_with_changeable_data(self):
        """Проверка доступности для страниц с изменяемыми данными."""
        post_urls = {
            f'/posts/{TestUrl.post.pk}/edit/': {
                self.author_client: HTTPStatus.OK,
            },
            '/create/': {
                self.auth_client: HTTPStatus.OK,
                self.author_client: HTTPStatus.OK,
            }
        }

        for url, clients in post_urls.items():
            for client, status in clients.items():
                with self.subTest(url=url):
                    response = client.get(url)
                    self.assertEqual(
                        response.status_code,
                        status,
                    )

    def test_template_available_to_everyone(self):
        """Проверим шаблоны доступные для всех пользователей."""
        templates = {
            '/': 'posts/index.html',
            f'/group/{TestUrl.group.slug}/': 'posts/group_list.html',
            f'/profile/{TestUrl.user.username}/': 'posts/profile.html',
            f'/posts/{TestUrl.post.pk}/': 'posts/post_detail.html',
        }

        for url, template in templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_template_availability_of_with_changeable_data(self):
        """Проверим шаблоны для изменяемых данных.

        будем проверять на авторизованном пользователе, авторе
        """
        templates = {
            f'/posts/{TestUrl.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for url, template in templates.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_redirect_for_anonimus_user(self):
        """Проверим редирект для неавторизованного пользователя."""
        redirect_urls = {
            f'/posts/{TestUrl.post.pk}/edit/': '/auth/login/?next=',
            '/create/': '/auth/login/?next=',
        }

        for url, redirect in redirect_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect + url)

    def test_redirect_for_not_author(self):
        """Проверим редирект для авторизованного пользователя но не автора."""
        response = self.auth_client.get(f'/posts/{TestUrl.post.pk}/edit/')
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': TestUrl.post.pk}
        ))
