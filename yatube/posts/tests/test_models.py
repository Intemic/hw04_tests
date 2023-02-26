from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class TestModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост проверим длинну сохраняемого текста',
        )

    def test_text_length_post(self):
        len_text = len(str(TestModel.post))
        self.assertEquals(len_text, 15, 'Некорректная длина текста')

    def test_text_value_post(self):
        self.assertEquals(
            str(TestModel.post),
            TestModel.post.text[:15],
            'Некорректное значение текста __str__'
        )

    def test_text_value_group(self):
        self.assertEquals(
            str(TestModel.group),
            TestModel.group.title,
            'Некорректное значение текста __str__'
        )

    def test_verbose_name(self):
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }

        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    TestModel.post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        field_help_texts = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    TestModel.post._meta.get_field(field).help_text,
                    expected_value
                )
