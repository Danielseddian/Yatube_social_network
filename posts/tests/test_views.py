import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User
from yatube.settings import POSTS_COUNT

AUTHOR_USERNAME = 'Pushkin'
GROUP_TITLE = 'Poet'
GROUP_SLUG = 'poet'
MAIN_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:new_post')
FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR_USERNAME])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[AUTHOR_USERNAME])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])
GROUP_URL = reverse('posts:group_posts', args=[GROUP_SLUG])
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class TestView(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.guest = Client()
        cls.author = Client()
        cls.not_author = Client()
        cls.author_user = User.objects.create(username=AUTHOR_USERNAME)
        cls.author.force_login(cls.author_user)
        cls.not_author_user = User.objects.create(username='Block')
        cls.not_author.force_login(cls.not_author_user)
        cls.not_author.get(FOLLOW_URL)
        cls.group = Group.objects.create(title=GROUP_TITLE,
                                         slug=GROUP_SLUG)
        other_group = Group.objects.create(title='Writer', slug='writer')
        image = SimpleUploadedFile(
            name='image.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author_user,
            group=cls.group,
            image=image
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.author_user,
            post=cls.post
        )
        author = cls.author_user
        cls.POST_URL = reverse('posts:post_view',
                               args=[author.username, cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[AUTHOR_USERNAME,
                                                             cls.post.id])
        cls.OTHER_GROUP_URL = reverse('posts:group_posts',
                                      args=[other_group.slug])
        cls.COMMENTS_URL = reverse('posts:add_comment',
                                   args=[author.username, cls.post.id])

    def test_paginator_for_ten_and_four_items(self):
        """Провеяем, что paginator работает правильно."""
        posts_count = 3
        posts = (Post(text='Тестовый текст %s' % number,
                      author=self.author_user,
                      group=self.group) for number in range(POSTS_COUNT
                                                            + posts_count))
        Post.objects.bulk_create(posts)
        comments = (Comment(text='Тестовый комментарий %s' % number,
                            author=self.author_user,
                            post=self.post) for number in range(POSTS_COUNT
                                                                + posts_count))
        Comment.objects.bulk_create(comments)
        reversed_items = {
            MAIN_URL: POSTS_COUNT,
            MAIN_URL + '?page=2': posts_count + 1,
            GROUP_URL: POSTS_COUNT,
            GROUP_URL + '?page=2': posts_count + 1,
            PROFILE_URL: POSTS_COUNT,
            PROFILE_URL + '?page=2': posts_count + 1,
            self.POST_URL: POSTS_COUNT,
            self.POST_URL + '?page=2': posts_count + 1,
            self.COMMENTS_URL: POSTS_COUNT,
            self.COMMENTS_URL + '?page=2': posts_count + 1,
            FOLLOW_INDEX_URL: POSTS_COUNT,
            FOLLOW_INDEX_URL + '?page=2': posts_count + 1,
        }
        for url, page_posts_count in reversed_items.items():
            with self.subTest(url=url):
                self.assertEqual(len(
                    self.not_author.get(url).context['page']
                ), page_posts_count)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_response_correct_context_for_pages(self):
        """Провеяем, что посты на страницах возвращают ожидаемый контекст."""
        items = {
            MAIN_URL: 'page',
            GROUP_URL: 'page',
            PROFILE_URL: 'page',
            FOLLOW_INDEX_URL: 'page',
            self.POST_URL: 'post',
        }
        for url, value in items.items():
            response = self.not_author.get(url)
            with self.subTest(url=url):
                if value == 'page':
                    posts = response.context[value]
                    self.assertEqual(len(posts), 1)
                    post = posts[0]
                else:
                    post = response.context[value]
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.image.name, self.post.image.name)

    def test_response_correct_context_for_comments(self):
        """Провеяем, что каменты на страницах возвращают ожидаемый контекст."""
        items = {
            self.POST_URL: 'page',
            self.COMMENTS_URL: 'page',
        }
        for url, value in items.items():
            response = self.author.get(url)
            with self.subTest(url=url):
                comments = response.context[value]
                self.assertEqual(len(comments), 1)
                comment = comments[0]
                self.assertEqual(comment.text, self.comment.text)
                self.assertEqual(comment.author, self.comment.author)
                self.assertEqual(comment.post, self.post)

    def test_correct_cache_context_for_index(self):
        """Провеяем, что кеширование на главной странице работает."""
        primary_response = self.author.get(MAIN_URL).content
        self.author.post(NEW_POST_URL, data={'text': 'Новый текст'},
                         follow=True)
        secondary_response = self.author.get(MAIN_URL).content
        self.assertEqual(primary_response, secondary_response)
        cache.clear()
        third_response = self.author.get(MAIN_URL).content
        self.assertNotEqual(primary_response, third_response)

    def test_group_page_contains_current_posts(self):
        """Проверяем, что пост находится на странице только своей группы."""
        response = self.author.get(self.OTHER_GROUP_URL).context['page']
        self.assertNotIn(self.post, response)

    def test_author_context(self):
        """Проверяем, что автор правильно передаётся в контекст."""
        urls = [PROFILE_URL, self.POST_URL]

        for url in urls:
            with self.subTest(url=url):
                author = self.author.get(url).context['author']
                self.assertEqual(author.username, self.author_user.username)
                self.assertEqual(author.id, self.author_user.id)

    def test_group_context(self):
        """Проверяем, что группа правильно передаётся в контекст."""
        group = self.author.get(GROUP_URL).context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.id, self.group.id)
        self.assertEqual(group.description, self.group.description)

    def test_follow_index_context(self):
        """Проверяем, что пост не появляется в ленте неподписчика."""
        self.not_author.get(UNFOLLOW_URL)
        response = self.not_author.get(FOLLOW_INDEX_URL).context['page']
        for post in response:
            self.assertNotEqual(post.author.username,
                                self.author_user.username)
