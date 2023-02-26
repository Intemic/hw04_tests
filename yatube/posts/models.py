from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(verbose_name='Имя', max_length=200)
    slug = models.SlugField(verbose_name='Идентификатор', unique=True)
    description = models.TextField(verbose_name='Описание')

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        help_text='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts',
        help_text='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Сообщество',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        help_text='Группа, к которой будет относиться пост'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.text[:15]
