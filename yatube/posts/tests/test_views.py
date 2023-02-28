from django.conf import settings
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.forms import PostForm
from posts.models import Group, Post, User


class TestView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        # cls.authors = {
        #     'pshk': User.objects.create_user(username='pshk'),
        #     'leo': User.objects.create_user(username='leo'),
        # }
        # cls.group1 = Group.objects.create(
        #     title='Group1',
        #     slug='group1',
        #     description='Group1'
        # )
        #     'gr2': Group.objects.create(
        #         title='Group2',
        #         slug='group2',
        #         description='Group2'
        #     )
        # }

        # cls.count_post = (settings.NUMBER_OF_LINES_ON_PAGE
        #                   + round(settings.NUMBER_OF_LINES_ON_PAGE / 2))
        # набор постов от одного автора, группы
        # for i in range(1, cls.count_post):
        #     Post.objects.create(
        #         text='Пост № ' + str(i),
        #         author=TestView.authors['pshk'],
        #         group=TestView.groups['gr1']
        #     )

        # # создание поста с другими значениями автора, группы
        # cls.post_others = Post.objects.create(
        #     text='999',
        #     author=TestView.authors['leo'],
        #     group=TestView.groups['gr2']
        # )

    @classmethod
    def get_url_data(
            cls,
            group: Group,
            username: str,
            post_id: int = 1) -> list:
        """Формируем перечень url их шаблонов и контекста."""
        return (
            (
                reverse('posts:index'),
                'posts/index.html',
                {'page_obj': Page}
            ),

            (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': group.slug}
                ),
                'posts/group_list.html',
                {'group': Group, 'page_obj': Page}
            ),

            (
                reverse(
                    'posts:profile',
                    kwargs={'username': username}
                ),
                'posts/profile.html',
                {'author': User, 'page_obj': Page}
            ),

            (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': post_id}
                ),
                'posts/post_detail.html',
                {'post': Post}
            ),

            (
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': post_id}
                ),
                'posts/create_post.html',

                {'is_edit': bool, 'form': PostForm}
            ),

            (
                reverse('posts:post_create'),
                'posts/create_post.html',
                {'form': PostForm}
            )
        )

    def setUp(self):
        self.user_pshk = User.objects.create_user(username='pshk')

        self.author_client = Client()
        self.author_client.force_login(self.user_pshk)

        # self.author_client_leo = Client()
        # self.author_client_leo.force_login(TestView.authors['leo'])

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

        # self.urls = TestView.get_url_data(
        #     group=TestView.groups['gr1'],
        #     username=TestView.authors['pshk'].username)

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
        page_post = page.object_list[0]

        self.assertEqual(page_post.text, self.post.text)
        self.assertEqual(page_post.group, self.post.group)
        self.assertEqual(page_post.author, self.post.author)

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

        # провери обратное
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
        page_post = page.object_list[0]
        self.assertEqual(page_post.text, self.post.text)
        self.assertEqual(page_post.group, self.post.group)
        self.assertEqual(page_post.author, self.post.author)

        self.assertEqual(group.title, self.post.group.title)
        self.assertEqual(group.slug, self.post.group.slug)
        self.assertEqual(group.description, self.post.group.description)

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

        # провери обратное
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
        page_post = page.object_list[0]
        self.assertEqual(page_post.text, self.post.text)
        self.assertEqual(page_post.group, self.post.group)
        self.assertEqual(page_post.author.username, self.post.author.username)

        self.assertEqual(author.username, self.post.author.username)

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

        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)
        self.assertEqual(post.author.username, self.post.author.username)

    def test_post_edit_page(self):
        """Проверка страницы редактирования(контекст, шаблон, данные)."""
        url = reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}
        )

        response = self.author_client.get(url)
        self.assertTemplateUsed(response, 'posts/create_post.html')

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













    def test_of_using_correct_templates(self):
        """Проверка соответствия шаблонов."""
        for url, template, dict_ in self.urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_context_element_name_and_type(self):
        """Проверим на соответствие контекста(тип, наличие данных)."""
        for url, template, dict_ in self.urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                for elem, type_elem in dict(dict_).items():
                    self.assertIsInstance(
                        response.context.get(elem),
                        type_elem
                    )

    def test_paginator(self):
        """Проверим корректную работу paginatora."""
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
                        author=TestView.authors['pshk'],
                        group=TestView.groups['gr1']
                    )
                )

        Post.objects.bulk_create(post_list)

        # из кортежа возмем все пути в которых есть paginator
        for url, template, dict_ in self.urls:
            for elem, type_elem in dict(dict_).items():
                if type_elem is Page:
                    for page_n, count_post_in_page in page_count_post:
                        with self.subTest(url=url):
                            response = self.author_client.get(
                                url, [('page', page_n)]
                            )
                            self.assertEqual(
                                len(response.context[elem]),
                                count_post_in_page
                            )

    def test_create_post(self):
        """Проверим правильность создания поста."""
        self.urls = TestView.get_url_data(
            group=TestView.groups['gr2'],
            username=TestView.authors['leo'].username)

        for url, template, dict_ in self.urls:
            for elem, type_elem in dict(dict_).items():
                if type_elem is Page:
                    with self.subTest(url=url):
                        response = self.author_client.get(url)
                        page = response.context.get(elem)
                        self.assertIn(self.post_others, page.object_list)

    def test_correct_context_in_group_list(self):
        """Проверка раздела group_list на корретное содержимое."""
        response = self.author_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': TestView.groups['gr2'].slug}
            ),
        )
        obj = response.context.get('page_obj')
        self.assertEqual(len(obj), 1)
        self.assertEqual(obj[0].group, TestView.groups['gr2'])

    def test_correct_context_in_profile(self):
        """Проверка раздела profile на корретное содержимое."""
        response = self.author_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': TestView.authors['leo']}
            ),
        )
        obj = response.context.get('page_obj')
        self.assertEqual(len(obj), 1)
        self.assertEqual(obj[0].author, TestView.authors['leo'])

    def test_correct_context_for_post_id(self):
        """Проверка раздела post_detail на корретное содержимое."""
        urls = (
            reverse(
                'posts:post_detail',
                kwargs={'post_id': 2}
            ),

            reverse(
                'posts:post_edit',
                kwargs={'post_id': 2}
            ),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                # если это не редактирование
                if url.find('edit') == -1:
                    obj = response.context.get('post')
                else:
                    obj = response.context.get('form').instance
                self.assertEqual(obj.pk, 2)
