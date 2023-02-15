from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


URL_INDEX = reverse("posts:index")
GROUP_SLUG = "testgroup"
URL_GROUP = reverse("posts:group_list", args=[GROUP_SLUG])
AUTHOR_USERNAME = "Alex"
URL_AUTHOR = reverse("posts:profile", args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse("posts:post_create")


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="AUTHOR_USERNAME")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug=GROUP_SLUG,
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает str."""
        self.assertEqual(PostModelTest.post.text[:15], str(PostModelTest.post))
        self.assertEqual(PostModelTest.group.title, str(PostModelTest.group))
