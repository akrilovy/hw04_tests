from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


from posts.models import User, Post, Group


URL_INDEX = reverse("posts:index")
GROUP_SLUG = "testgroup"
URL_GROUP = reverse("posts:group_list", args=[GROUP_SLUG])
AUTHOR_USERNAME = "Alex"
URL_AUTHOR = reverse("posts:profile", args=[AUTHOR_USERNAME])
URL_CREATE_POST = reverse("posts:post_create")


class PostURLTests(TestCase):
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
            text="Test post", author=cls.test_post_author
        )
        cls.URL_POST_DETAIL = reverse(
            "posts:post_detail", args=[cls.test_post.id]
        )
        cls.URL_POST_EDIT = reverse("posts:edit", args=[cls.test_post.id])

    def setUp(self) -> None:
        self.user = User.objects.create_user(username="TestUser")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.test_post_author)

    def test_posts_urls(self):
        """
        Тест, который проверяет, что страницы доступы различным пользователям,
        т.е возвращает ожидаемый статус ответа.

        """
        address_client_status = [
            (URL_INDEX, self.client, HTTPStatus.OK),
            (URL_GROUP, self.client, HTTPStatus.OK),
            (URL_AUTHOR, self.client, HTTPStatus.OK),
            (URL_CREATE_POST, self.authorized_client, HTTPStatus.OK),
            (URL_CREATE_POST, self.client, HTTPStatus.FOUND),
            (PostURLTests.URL_POST_DETAIL, self.client, HTTPStatus.OK),
            (PostURLTests.URL_POST_EDIT, self.author_client, HTTPStatus.OK),
            (PostURLTests.URL_POST_EDIT, self.client, HTTPStatus.FOUND),
            (
                PostURLTests.URL_POST_EDIT,
                self.authorized_client,
                HTTPStatus.FOUND,
            ),
        ]
        for url_test in address_client_status:
            address, client, status = url_test
            self.assertEqual(
                client.get(address).status_code,
                status,
                f"{address} для {client} возвращается неверный код ответа",
            )
            self.assertTemplateUsed

    def test_posts_urls_use_expected_templated(self):
        address_template = [
            (URL_INDEX, "posts/index.html"),
            (URL_GROUP, "posts/group_list.html"),
            (URL_AUTHOR, "posts/profile.html"),
            (URL_CREATE_POST, "posts/create_post.html"),
            (PostURLTests.URL_POST_DETAIL, "posts/post_detail.html"),
            (PostURLTests.URL_POST_EDIT, "posts/create_post.html"),
        ]
        for address, template in address_template:
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(
                    response, template, f"неверный шаблон для адреса {address}"
                )
