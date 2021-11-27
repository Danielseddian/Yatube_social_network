from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

AUTHOR_USERNAME = 'Pushkin'
GROUP_TITLE = 'Poet'
GROUP_SLUG = 'poet'
MAIN_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
GROUP_URL = reverse('posts:group_posts', args=[GROUP_SLUG])
AUTH_REDIRECT_URL = reverse('login') + '?next='
NEW_FORM_URL = reverse('posts:new_post')
FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR_USERNAME])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[AUTHOR_USERNAME])
FOLLOW_INDEX_URL = reverse('posts:follow_index')


class TestUrls(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = Client()
        cls.author_user = User.objects.create(username=AUTHOR_USERNAME)
        cls.author.force_login(cls.author_user)
        cls.group = Group.objects.create(title=GROUP_TITLE,
                                         slug=GROUP_SLUG)
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author_user,
            group=cls.group
        )
        cls.guest = Client()
        username = cls.author_user.username
        post_id = cls.post.id
        cls.not_author = Client()
        not_author_user = User.objects.create(username='Block')
        cls.not_author.force_login(not_author_user)
        cls.POST_URL = reverse('posts:post_view',
                               args=[username, post_id])
        cls.POST_EDIT_URL = reverse('posts:post_edit',
                                    args=[username, post_id])
        cls.POST_COMMENT_URL = reverse('posts:add_comment',
                                       args=[username, post_id])

    def test_accesses_redirects(self):
        """Проверяем редиректы с недоступных страниц."""
        tested_urls = [
            [self.guest, self.POST_EDIT_URL, (AUTH_REDIRECT_URL
                                              + self.POST_EDIT_URL)],
            [self.guest, NEW_FORM_URL, (AUTH_REDIRECT_URL + NEW_FORM_URL)],
            [self.not_author, self.POST_EDIT_URL, self.POST_URL],
            [self.guest, FOLLOW_URL, (AUTH_REDIRECT_URL + FOLLOW_URL)],
            [self.guest, UNFOLLOW_URL, (AUTH_REDIRECT_URL + UNFOLLOW_URL)],
            [self.guest, self.POST_COMMENT_URL, (AUTH_REDIRECT_URL
                                                 + self.POST_COMMENT_URL)],
            [self.author, FOLLOW_URL, PROFILE_URL],
            [self.author, UNFOLLOW_URL, PROFILE_URL],
        ]
        for client, url, redirected in tested_urls:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True), redirected)

    def test_accesses_for_urls(self):
        """Проверяем, что коды запросов отвечают ожиданиям."""
        tested_urls = [
            [self.guest, MAIN_URL, 200],
            [self.guest, GROUP_URL, 200],
            [self.guest, PROFILE_URL, 200],
            [self.guest, self.POST_URL, 200],
            [self.guest, AUTH_REDIRECT_URL + NEW_FORM_URL, 200],
            [self.guest, AUTH_REDIRECT_URL + self.POST_EDIT_URL, 200],
            [self.author, FOLLOW_INDEX_URL, 200],
            [self.author, NEW_FORM_URL, 200],
            [self.author, self.POST_EDIT_URL, 200],
            [self.author, self.POST_COMMENT_URL, 200],
            [self.not_author, self.POST_COMMENT_URL, 200],
            [self.guest, self.POST_EDIT_URL, 302],
            [self.guest, NEW_FORM_URL, 302],
            [self.guest, FOLLOW_INDEX_URL, 302],
            [self.guest, FOLLOW_URL, 302],
            [self.guest, UNFOLLOW_URL, 302],
            [self.guest, self.POST_COMMENT_URL, 302],
            [self.author, FOLLOW_URL, 302],
            [self.author, UNFOLLOW_URL, 302],
            [self.not_author, self.POST_EDIT_URL, 302],
        ]
        for client, url, code in tested_urls:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code,
                                 code)

    def test_correct_template_in_response(self):
        """Проверяем соответствие шаблона запрашиваемому адресу."""
        templates_urls = [
            [self.author, MAIN_URL, 'index.html'],
            [self.author, GROUP_URL, 'group.html'],
            [self.author, NEW_FORM_URL, 'new.html'],
            [self.author, self.POST_EDIT_URL, 'new.html'],
            [self.author, self.POST_URL, 'post.html'],
            [self.author, PROFILE_URL, 'profile.html'],
            [self.author, self.POST_COMMENT_URL, 'includes/comments.html'],
            [self.author, FOLLOW_INDEX_URL, 'follow.html'],
        ]
        for client, url, template in templates_urls:
            with self.subTest(url=url):
                self.assertTemplateUsed(client.get(url), template)
