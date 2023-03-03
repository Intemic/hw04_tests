import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Post, Group, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestForm(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author_user = User.objects.create_user(username='leo')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def create_post_with_image(self) -> Post:
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

        return Post.objects.create(
            text='Пост 1',
            author=TestForm.author_user,
            group=self.group,
            image=upload_image
        )

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

    def test_display_image_on_main_page(self):
        # так как у нас проверяется одна и та же функциональность
        # попробуем так, вроде атомарность не нарушаем 
        post = self.create_post_with_image()
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
                    kwargs={'username': TestForm.author_user.username}
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
                print(obj.image) 


