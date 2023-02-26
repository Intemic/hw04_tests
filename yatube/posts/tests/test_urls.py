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
            text='Тестовый пост про чтот то',
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
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': TestUrl.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': TestUrl.user.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': TestUrl.post.pk}
            ): HTTPStatus.OK,
            'unexisting_page/': HTTPStatus.NOT_FOUND,
        }

        for url, result in post_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    result,
                )

    def test_availability_of_url_with_changeable_data(self):
        """Проверка соответствия прав доступа различным типам пользователей.

        для страниц с изменяемыми данными.
        """
        post_urls = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': TestUrl.post.pk}
            ): {
                self.guest_client: HTTPStatus.FOUND,
                self.auth_client: HTTPStatus.FOUND,
                self.author_client: HTTPStatus.OK,
            },
            reverse('posts:post_create'): {
                self.guest_client: HTTPStatus.FOUND,
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
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': TestUrl.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': TestUrl.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': TestUrl.post.pk}
            ): 'posts/post_detail.html',
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
            reverse(
                'posts:post_edit',
                kwargs={'post_id': TestUrl.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for url, template in templates.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_redirect_for_anonimus_user(self):
        """Проверим редирект для неавторизованного пользователя."""
        redirect_urls = {
            reverse(
                'posts:post_edit',
                kwargs={'post_id': TestUrl.post.pk}
            ): '/auth/login/?next=',
            reverse('posts:post_create'): '/auth/login/?next=',
        }

        for url, redirect in redirect_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, redirect + url)

    def test_redirect_for_not_author(self):
        """Проверим редирект для авторизованного пользователя но не автора."""
        url = reverse(
            'posts:post_edit',
            kwargs={'post_id': TestUrl.post.pk}
        )
        response = self.auth_client.get(url)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': TestUrl.post.pk}
        ))
