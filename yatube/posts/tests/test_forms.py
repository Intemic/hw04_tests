from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User


class TestForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author_user = User.objects.create_user(username='leo')

    def setUp(self) -> None:
        self.author_client = Client()
        self.author_client.force_login(TestForm.author_user)

        self.group = Group.objects.create(
            title='Group1',
            slug='group1',
            description='Group1'
        )

    def test_create_post(self):
        """Проверка корректности создания поста."""
        count_post = Post.objects.count()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.pk
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), count_post + 1)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': TestForm.author_user.username})
        )
        post: Post = Post.objects.all()[0]
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, Group.objects.get(pk=form_data['group']))

    def test_edit_post(self):
        """Проверка корректной работы измененеия поста."""
        post = Post.objects.create(
            text='Просто пост',
            author=self.author_user,
        )

        count_post = Post.objects.count()
        form_data = {
            'text': 'Изменененый текст',
            'group': self.group.pk
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(pk=post.pk)

        self.assertEqual(Post.objects.count(), count_post)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, Group.objects.get(pk=form_data['group']))
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': post.pk})
        )
