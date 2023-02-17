from django import forms
from django.urls import reverse
from django.test import TestCase, Client


from posts.models import Post, Group, User


URL_INDEX = reverse("posts:index")
GROUP_SLUG = "testgroup"
URL_GROUP = reverse("posts:group_list", args=[GROUP_SLUG])
AUTHOR_USERNAME = "Alex"
URL_AUTHOR = reverse("posts:profile", args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse("posts:post_create")


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_author = User.objects.create_user(
            username=AUTHOR_USERNAME
        )
        cls.test_group = Group.objects.create(
            title="Test group", slug=GROUP_SLUG, description="Test desc"
        )
        cls.test_group_2 = Group.objects.create(
            title="Test group", slug="test_slug_2", description="Test desc"
        )
        cls.test_post = Post.objects.create(
            text="Test post", author=cls.test_post_author, group=cls.test_group
        )
        cls.URL_POST_DETAIL = reverse(
            "posts:post_detail", args=[cls.test_post.id]
        )
        cls.URL_POST_EDIT = reverse("posts:edit", args=[cls.test_post.id])

    def setUp(self) -> None:
        self.author_client = Client()
        self.author_client.force_login(PostFormTest.test_post_author)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "тестовый текст поста",
            "group": PostFormTest.test_group.pk,
        }
        response = self.author_client.post(
            URL_CREATE_POST, data=form_data, follow=True
        )
        now_count = Post.objects.count()
        self.assertEqual(posts_count + 1, now_count)
        self.assertRedirects(response, URL_AUTHOR)
        added_post = Post.objects.latest("id")
        self.assertEqual(added_post.text, form_data["text"])
        self.assertEqual(added_post.group.pk, form_data["group"])
        self.assertEqual(added_post.author, PostFormTest.test_post_author)

    def test_edit_post_by_author(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "тестовый текст поста (изменение)",
            "group": PostFormTest.test_group_2.pk,
        }
        response = self.author_client.post(
            PostFormTest.URL_POST_EDIT, data=form_data, follow=True
        )
        now_count = Post.objects.count()

        self.assertEqual(posts_count, now_count)
        self.assertRedirects(response, PostFormTest.URL_POST_DETAIL)

        edited_post = Post.objects.get(id=PostFormTest.test_post.id)
        self.assertEqual(edited_post.text, form_data["text"])
        self.assertEqual(edited_post.group.pk, form_data["group"])

    def test_create_edit_form_fields_type(self):
        addresses = [URL_CREATE_POST, PostFormTest.URL_POST_EDIT]
        form_fields = (
            ("text", forms.fields.CharField),
            ("group", forms.fields.ChoiceField),
        )
        for address in addresses:
            response = self.author_client.get(address)
            for field, expected_type in form_fields:
                field_type = response.context.get("form").fields.get(field)
                self.assertIsInstance(
                    field_type,
                    expected_type,
                    f"Неверний тип для поля формы - {field}",
                )
