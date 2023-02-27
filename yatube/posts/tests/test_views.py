from django.conf import settings
from django.core.paginator import Page
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User


class TestView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.authors = {
            'pshk': User.objects.create_user(username='pshk'),
            'leo': User.objects.create_user(username='leo'),
        }
        cls.groups = {
            'gr1': Group.objects.create(
                title='Group1',
                slug='group1',
                description='Group1'
            ),
            'gr2': Group.objects.create(
                title='Group2',
                slug='group2',
                description='Group2'
            )
        }

        cls.author_client = Client()
        cls.author_client.force_login(TestView.authors['pshk'])

        cls.author_client_leo = Client()
        cls.author_client_leo.force_login(TestView.authors['leo'])

        cls.count_post = (settings.NUMBER_OF_LINES_ON_PAGE
                          + round(settings.NUMBER_OF_LINES_ON_PAGE / 2))

        # набор постов от одного автора, группы
        for i in range(1, cls.count_post):
            Post.objects.create(
                text='Пост № ' + str(i),
                author=TestView.authors['pshk'],
                group=TestView.groups['gr1']
            )

        # создание поста с другими значениями автора, группы
        cls.post_others = Post.objects.create(
            text='999',
            author=TestView.authors['leo'],
            group=TestView.groups['gr2']
        )

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

    def setUp(self) -> None:
        self.urls = TestView.get_url_data(
            group=TestView.groups['gr1'],
            username=TestView.authors['pshk'].username)

    def test_of_using_correct_templates(self):
        """Проверка соответствия шаблонов."""
        for url, template, dict_ in self.urls:
            with self.subTest(url=url):
                response = TestView.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_context_element_name_and_type(self):
        """Проверим на соответствие контекста(тип, наличие данных)."""
        for url, template, dict_ in self.urls:
            with self.subTest(url=url):
                response = TestView.author_client.get(url)
                for elem, type_elem in dict(dict_).items():
                    self.assertIsInstance(
                        response.context.get(elem),
                        type_elem
                    )
                    self.assertIsNotNone(response.context.get(elem))

    def test_paginator(self):
        """Проверим корректную работу paginatora."""
        for url, template, dict_ in self.urls:
            for elem, type_elem in dict(dict_).items():
                if type_elem is Page:
                    for page_n in range(1, 3):
                        if page_n == 1:
                            count_post_in_page = (settings.
                                                  NUMBER_OF_LINES_ON_PAGE)
                        else:
                            count_post_in_page = (TestView.count_post
                                                  - settings.
                                                  NUMBER_OF_LINES_ON_PAGE)
                            # если не главная то откинем один пост
                            if url != reverse('posts:index'):
                                count_post_in_page = count_post_in_page - 1

                        with self.subTest(url=url):
                            response = TestView.author_client.get(
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
                        response = TestView.author_client.get(url)
                        page = response.context.get(elem)
                        self.assertIn(self.post_others, page.object_list)

    def test_correct_context_in_group_list(self):
        """Проверка раздела group_list на корретное содержимое."""
        response = TestView.author_client.get(
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
        response = TestView.author_client.get(
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
            print(url)
            with self.subTest(url=url):
                response = TestView.author_client.get(url)
                # если это не редактирование
                if url.find('edit') == -1:
                    obj = response.context.get('post')
                else:
                    obj = response.context.get('form').instance
                self.assertEqual(obj.pk, 2)
