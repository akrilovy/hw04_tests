from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField("адрес", unique=True)
    description = models.TextField("описание")

    def __str__(self) -> str:
        return str(self.title)


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )  

    def __str__(self) -> str:
        return self.text[:15]

    def __eq__(self, other) -> bool:
        return self.id == other.id

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий к посту',
        help_text='Для какого поста этот комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Кто автор этого комментария'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        max_length=140,
        help_text='Введите текст от 3-х до 140 символов',
        blank=False,
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время комментария',
        help_text='Завполняется автоматически'
    )