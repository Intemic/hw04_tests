from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User


class TestForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author_user = User.objects.create_user(username='leo')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author_user)
        cls.post = Post.objects.create(
            text='Просто пост',
            author=cls.author_user,
        )

    def test_create_post(self):
        """Проверка корректности создания поста."""
        count_post = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
        }
        response = TestForm.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), count_post + 1)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': TestForm.author_user.username})
        )

    def test_edit_post(self):
        """Проверка корректной работы измененеия поста."""
        text_post = 'Изменененый текст'
        form_data = {
            'text': text_post
        }
        response = TestForm.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': TestForm.post.pk}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=TestForm.post.pk)
        self.assertEqual(post.text, text_post)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': TestForm.post.pk})
        )
