from django.conf import settings
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.forms import PostForm
from posts.models import Group, Post, User


class TestView(TestCase):
    def compare_posts(self, post: Post, post_ref: Post) -> None:
        self.assertEqual(post.text, post_ref.text)
        self.assertEqual(post.group, post_ref.group)
        self.assertEqual(post.author, post_ref.author)

    def compare_groups(self, group: Group, group_ref: Group) -> None:
        self.assertEqual(group.title, group_ref.title)
        self.assertEqual(group.slug, group_ref.slug)
        self.assertEqual(group.description, group_ref.description)

    def setUp(self):
        self.user_pshk = User.objects.create_user(username='pshk')

        self.author_client = Client()
        self.author_client.force_login(self.user_pshk)

        self.group1 = Group.objects.create(
            title='Group1',
            slug='group1',
            description='Group1'
        )

        self.post = Post.objects.create(
            text='Пост 1',
            author=self.user_pshk,
            group=self.group1
        )

    def tearDown(self) -> None:
        User.objects.all().delete()
        Group.objects.all().delete()
        Post.objects.all().delete()

    def test_main_page(self):
        """Проверка главной страницы(контекст, шаблон, данные)."""
        url = reverse('posts:index')
        response = self.author_client.get(url)

        self.assertTemplateUsed(response, 'posts/index.html')

        page = response.context.get('page_obj')
        self.assertIsInstance(page, Page)
        # сравним значения
        self.compare_posts(page.object_list[0], self.post)

    def test_group_list_page(self):
        """Проверка страницыe(контекст, шаблон, данные)."""
        # добавим еще одну группу
        group2 = Group.objects.create(
            title='Group2',
            slug='group2',
            description='Group2'
        )

        url = reverse(
            'posts:group_list',
            kwargs={'slug': group2.slug}
        )

        # проверим что пост не попал на другую страницу
        response = self.author_client.get(url)
        page = response.context.get('page_obj')
        self.assertNotIn(self.post, page.object_list)

        # проверим обратное
        url = reverse(
            'posts:group_list',
            kwargs={'slug': self.post.group.slug}
        )
        response = self.author_client.get(url)
        self.assertTemplateUsed(response, 'posts/group_list.html')

        page = response.context.get('page_obj')
        self.assertIsInstance(page, Page)
        group = response.context.get('group')
        self.assertIsInstance(group, Group)

        # проверим данные объекта и группу
        self.compare_posts(page.object_list[0], self.post)
        self.compare_groups(group, self.post.group)

    def test_profile_page(self):
        """Проверка профиля(контекст, шаблон, данные)."""
        # содаем второго пользователя
        user_leo = User.objects.create_user(username='leo')

        url = reverse(
            'posts:profile',
            kwargs={'username': user_leo.username}
        )

        # проверим что пост не попал на другую страницу
        response = self.author_client.get(url)
        page = response.context.get('page_obj')
        self.assertNotIn(self.post, page.object_list)

        # проверим обратное
        url = reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username}
        )

        response = self.author_client.get(url)
        self.assertTemplateUsed(response, 'posts/profile.html')

        page = response.context.get('page_obj')
        self.assertIsInstance(page, Page)
        author = response.context.get('author')
        self.assertIsInstance(author, User)

        # проверим данные объекта и автора
        self.compare_posts(page.object_list[0], self.post)
        self.assertEqual(author, self.post.author)

    def test_post_detail_page(self):
        """Проверка страницы поста(контекст, шаблон, данные)."""
        post2 = Post.objects.create(
            text='Пост 2',
            author=self.user_pshk,
            group=self.group1
        )

        url = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )

        response = self.author_client.get(url)
        self.assertTemplateUsed(response, 'posts/post_detail.html')

        post = response.context.get('post')
        self.assertIsInstance(post, Post)
        self.assertNotEqual(post.pk, post2.pk)

        self.compare_posts(post, self.post)

    def test_post_edit_page(self):
        """Проверка страницы редактирования(контекст, шаблон, данные)."""
        url = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        )

        response = self.author_client.get(url)
        self.assertTemplateUsed(response, 'posts/create_post.html')
        self.assertIsInstance(response.context['form'], PostForm)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

        self.assertIsInstance(response.context['is_edit'], bool)
        self.assertEqual(response.context['is_edit'], True)

    def test_create_page(self):
        """Проверка страницы создания поста(контекст, шаблон, данные)."""
        url = reverse('posts:post_create')

        response = self.author_client.get(url)
        self.assertTemplateUsed(response, 'posts/create_post.html')
        self.assertIsInstance(response.context['form'], PostForm)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_display_created_post(self):
        """Проверим правильность отображения нового поста.

        должен появляться на нужных страницах, в нужном количестве
        и с нужными данными
        """
        user_leo = User.objects.create_user(username='leo')
        group2 = Group.objects.create(
            title='Group2',
            slug='group2',
            description='Group2'
        )
        post2 = Post.objects.create(
            text='Пост 2',
            author=user_leo,
            group=group2
        )

        urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': group2.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': user_leo.username}
            ),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                page = response.context.get('page_obj')
                # проверим что наш пост попал
                self.assertIn(post2, page.object_list)
                # для главной должно быть 2
                if url == reverse('posts:index'):
                    self.assertEqual(len(page.object_list), 2)
                # для не главной страницы он один и соответствует ожиданиям
                else:
                    self.assertEqual(len(page.object_list), 1)
                    self.compare_posts(page.object_list[0], post2)

    def test_paginator(self):
        """Проверим корректную работу paginatora."""
        urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group1.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user_pshk.username}
            )
        )

        Post.objects.all().delete()

        page_count_post = (
            (1, settings.NUMBER_OF_LINES_ON_PAGE),
            (2, round(settings.NUMBER_OF_LINES_ON_PAGE / 2))
        )

        post_list = []
        for page, count in page_count_post:
            while count:
                count -= 1
                post_list.append(
                    Post(
                        text='Пост № ' + str(len(post_list) + 1),
                        author=self.user_pshk,
                        group=self.group1
                    )
                )

        Post.objects.bulk_create(post_list)

        for url in urls:
            for page_n, count_post_in_page in page_count_post:
                with self.subTest(url=url):
                    response = self.author_client.get(
                        url, [('page', page_n)]
                    )
                    self.assertEqual(
                        len(response.context['page_obj']),
                        count_post_in_page
                    )
