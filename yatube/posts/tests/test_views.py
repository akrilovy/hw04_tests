from django import forms
from django.test import Client, TestCase
from django.urls import reverse


from posts.models import Post, Group, User
from posts.views import POST_COUNT


URL_INDEX = reverse("posts:index")
GROUP_SLUG = "testgroup"
URL_GROUP = reverse("posts:group_list", args=[GROUP_SLUG])
AUTHOR_USERNAME = "Alex"
URL_AUTHOR = reverse("posts:profile", args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse("posts:post_create")


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_author = User.objects.create_user(
            username=AUTHOR_USERNAME
        )
        cls.test_group = Group.objects.create(
            title="Test group", slug=GROUP_SLUG, description="Test desc"
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
        self.author_client.force_login(PostPagesTests.test_post_author)

    def check_post_eq(self, post1, post2):
        self.assertEqual(post1.author, post2.author)
        self.assertEqual(post1.text, post2.text)
        self.assertEqual(post1.group, post2.group)
        self.assertEqual(
            post1.pk, post2.pk
        )  # TODO если pk совпадают, то совпадает всё?. Нужно ли остальное?

    def test_posts_pages_show_context(self):
        addresses = [
            URL_INDEX,
            URL_GROUP,
            URL_AUTHOR,
        ]
        for address in addresses:
            response = self.author_client.get(address)
            post = response.context.get("page_obj")[
                0
            ] 
            self.check_post_eq(post, PostPagesTests.test_post)

    def test_detail_show_correct_template(self):
        response = self.author_client.get(PostPagesTests.URL_POST_DETAIL)
        post = response.context.get("post")
        self.check_post_eq(post, PostPagesTests.test_post)

    def test_group_context(self):
        response = self.author_client.get(URL_GROUP)
        group = response.context.get("group")
        self.assertEqual(group.slug, PostPagesTests.test_group.slug)
        self.assertEqual(group.title, PostPagesTests.test_group.title)
        self.assertEqual(
            group.description, PostPagesTests.test_group.description
        )
        self.assertEqual(
            group.pk, PostPagesTests.test_group.pk
        )  # TODO если pk совпадают, то нужно ли проверять остальное?

    def test_profile_context(self):
        response = self.author_client.get(URL_AUTHOR)
        author = response.context.get("author")
        self.assertEqual(
            author.username, PostPagesTests.test_post_author.username
        )
        self.assertEqual(author.pk, PostPagesTests.test_post_author.pk)

    def test_create_edit_context(self):
        addresses = [URL_CREATE_POST, PostPagesTests.URL_POST_EDIT]
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

class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_post_author = User.objects.create_user(
            username=AUTHOR_USERNAME
        )
        cls.test_post_author_second = User.objects.create_user(
            username="test_username"
        )
        cls.test_group = Group.objects.create(
            title="Test group", slug=GROUP_SLUG, description="Test desc"
        )
        cls.test_group_2 = Group.objects.create(
            title="Test grou2", slug="slug2", description="Test desc2"
        )

        objs = [
            Post(
                author=cls.test_post_author,
                text=f"Текст поста первого автора - {i}",
                group=cls.test_group,
            )
            for i in range(9)
        ]
        Post.objects.bulk_create(objs)
        objs = [
            Post(
                author=cls.test_post_author_second,
                text=f"Текст поста первого автора - {i}",
            )
            for i in range(4)
        ]
        Post.objects.bulk_create(objs)

    def test_index_first_page(self):
        response = self.client.get(URL_INDEX)
        self.assertEqual(len(response.context["page_obj"]), POST_COUNT)

    def test_index_second_page(self):
        response = self.client.get(URL_INDEX + "?page=2")
        self.assertEqual(
            len(response.context["page_obj"]),
            (Post.objects.count() - POST_COUNT),
        )

    def test_group_page(self):
        response = self.client.get(URL_GROUP)
        self.assertEqual(
            len(response.context["page_obj"]),
            Post.objects.filter(group=PaginatorViewTest.test_group).count(),
        )

    def test_profile_page(self):
        response = self.client.get(URL_AUTHOR)
        self.assertEqual(
            len(response.context["page_obj"]),
            Post.objects.filter(
                author=PaginatorViewTest.test_post_author
            ).count(),
        )