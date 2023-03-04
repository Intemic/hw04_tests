import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.forms import PostForm
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_pshk = User.objects.create_user(username='pshk')
        cls.group1 = Group.objects.create(
            title='Group1',
            slug='group1',
            description='Group1'
        )
        cls.post = Post.objects.create(
            text='Пост 1',
            author=cls.user_pshk,
            group=cls.group1
        )

        cls.urls_pattern = (
            (
                reverse('posts:index'),
                'posts/index.html',
            ),

            (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': cls.group1.slug}
                ),
                'posts/group_list.html',
            ),

            (
                reverse(
                    'posts:profile',
                    kwargs={'username': cls.user_pshk.username}
                ),
                'posts/profile.html',
            ),

            (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': cls.post.pk}
                ),
                'posts/post_detail.html',
            ),

            (
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': cls.post.pk}
                ),
                'posts/create_post.html',
            ),

            (
                reverse('posts:post_create'),
                'posts/create_post.html',
            )
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def compare_posts(self, post: Post, post_ref: Post) -> None:
        self.assertIsInstance(post, Post)
        self.assertEqual(post.text, post_ref.text)
        self.assertEqual(post.group, post_ref.group)
        self.assertEqual(post.author, post_ref.author)

    def compare_groups(self, group: Group, group_ref: Group) -> None:
        self.assertIsInstance(group, Group)
        self.assertEqual(group.title, group_ref.title)
        self.assertEqual(group.slug, group_ref.slug)
        self.assertEqual(group.description, group_ref.description)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user_pshk)

    def test_patterns(self):
        """Проверяем шаблоны."""
        for url, pattern in TestView.urls_pattern:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, pattern)

    def test_main_page(self):
        """Проверка главной страницы(контекст, шаблон, данные)."""
        url = reverse('posts:index')
        response = self.author_client.get(url)

        page = response.context.get('page_obj')
        self.assertIsInstance(page, Page)
        # сравним значения
        self.compare_posts(page.object_list[0], self.post)

    def test_group_list_page(self):
        """Проверка страницы(контекст, шаблон, данные)."""
        url = reverse(
            'posts:group_list',
            kwargs={'slug': self.post.group.slug}
        )
        response = self.author_client.get(url)

        page = response.context.get('page_obj')
        self.assertIsInstance(page, Page)
        group = response.context.get('group')

        # проверим данные объекта и группу
        self.compare_posts(page.object_list[0], self.post)
        self.compare_groups(group, self.post.group)

    def test_profile_page(self):
        """Проверка профиля(контекст, шаблон, данные)."""
        url = reverse(
            'posts:profile',
            kwargs={'username': self.post.author.username}
        )

        response = self.author_client.get(url)

        page = response.context.get('page_obj')
        self.assertIsInstance(page, Page)
        author = response.context.get('author')
        self.assertIsInstance(author, User)

        # проверим данные объекта и автора
        self.compare_posts(page.object_list[0], self.post)
        self.assertEqual(author, self.post.author)

    def test_post_detail_page(self):
        """Проверка страницы поста(контекст, шаблон, данные)."""
        url = reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk}
        )

        response = self.author_client.get(url)

        post = response.context.get('post')
        self.compare_posts(post, self.post)

    def test_post_edit_page(self):
        """Проверка страницы редактирования(контекст, шаблон, данные)."""
        url = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        )

        response = self.author_client.get(url)
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
        # кол-во объектов на второй странице
        number_obj_on_secon_page = round(settings.NUMBER_OF_LINES_ON_PAGE / 2)
        count_objects = (settings.NUMBER_OF_LINES_ON_PAGE
                         + number_obj_on_secon_page)

        page_count_post = (
            (1, settings.NUMBER_OF_LINES_ON_PAGE),
            (2, number_obj_on_secon_page)
        )

        Post.objects.bulk_create(
            [
                Post(
                    text='Пост № ' + str(i + 1),
                    author=self.user_pshk,
                    group=self.group1
                ) for i in range(count_objects)
            ]
        )

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

    def test_for_not_posting_in_another_group(self):
        """Проверим что при наличии нескольких групп.

        пост не отображается в не свонй группе
        """
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

    def test_for_not_posting_in_another_user(self):
        """Проверим что при наличии нескольких пользователей.

        пост не отображается у другого user'a
        """
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

    def test_for_the_absence_of_another_post_on_detail_page(self):
        """Проверим что при наличии нескольких постов.

        не отображается другой
        """
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

        post = response.context.get('post')
        self.assertNotEqual(post.pk, post2.pk)

    def test_display_image_on_main_page(self):
        # так как у нас проверяется одна и та же функциональность
        # попробуем так, вроде атомарность не нарушаем
        # одну же функциональность проверяем
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        upload_image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        post = Post.objects.create(
            text='Пост 1',
            author=TestView.user_pshk, 
            group=TestView.group1,
            image=upload_image
        )    
    
        urls = (
            (
                reverse('posts:index'),
                'page_obj',
            ),

            (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': post.group.slug}
                ),
                'page_obj',
            ),

            (
                reverse(
                    'posts:profile',
                    kwargs={'username': TestView.user_pshk.username}
                ),
                'page_obj',
            ),

            (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': post.pk}
                ),
                'post',
            ),
        )

        for url, elem in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                obj = response.context.get(elem)
                if elem == 'page_obj':
                    obj = obj.object_list[0]
                self.assertEqual(obj.image.name, f'posts/{upload_image.name}') 

    def test_anonymous_user_cannot_comment(self):
        # TODO Реализовать "комментировать посты может только авторизованный пользователь"
        pass