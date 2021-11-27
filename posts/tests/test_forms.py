import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post, User

MAIN_URL = reverse('posts:index')
AUTH_REDIRECT_URL = reverse('login') + '?next='
NEW_FORM_URL = reverse('posts:new_post')
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class TestForm(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.MEDIA_ROOT)
        cls.guest = Client()
        cls.not_author = Client()
        cls.not_author_user = User.objects.create(username='Block')
        cls.not_author.force_login(cls.not_author_user)
        cls.author = Client()
        cls.author_user = User.objects.create(username='Pushkin')
        cls.author.force_login(cls.author_user)
        group = Group.objects.create(title='Poet', slug='poet')
        image = SimpleUploadedFile(
            name='image.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.author_user,
            group=group,
            image=image
        )
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[
            cls.post.author.username, cls.post.id
        ])
        cls.POST_VIEW_URL = reverse('posts:post_view', args=[
            cls.post.author.username, cls.post.id
        ])
        cls.COMMENT_URL = reverse('posts:add_comment', args=[
            cls.post.author.username, cls.post.id
        ])
        new_group = Group.objects.create(title='Writer', slug='writer')
        cls.upload_data = {
            'group': new_group.pk,
            'text': 'Новый текст',
        }
        cls.comment_data = {'text': 'Тестовый комментарий'}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_new_form_for_guest(self):
        """Тестируем форму создания новой записи для гостя."""
        primary_posts = list(Post.objects.all())
        posts_count = Post.objects.count()
        response = self.guest.post(
            NEW_FORM_URL,
            data=self.upload_data,
            follow=True
        )
        self.assertRedirects(response,
                             AUTH_REDIRECT_URL + NEW_FORM_URL)
        self.assertEqual(set(Post.objects.all()), set(primary_posts))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, 200)

    def test_new_form_for_user(self):
        """Тестируем форму создания новой записи для пользователя."""
        primary_keys = [value.pk for value in Post.objects.all()]
        self.upload_data['image'] = SimpleUploadedFile(
            name='new_form_image.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        response = self.author.post(
            NEW_FORM_URL,
            data=self.upload_data,
            follow=True
        )
        self.assertRedirects(response, MAIN_URL)
        keys = [value.pk for value in Post.objects.all()
                if value.pk not in primary_keys]
        self.assertEqual(len(keys), 1)
        post = Post.objects.get(id=keys[0])
        contexts = {
            post.group.id: self.upload_data['group'],
            post.author: self.author_user,
            post.text: self.upload_data['text'],
            post.image.name: 'posts/' + self.upload_data['image'].name,
            response.status_code: 200,
        }
        for context, expected in contexts.items():
            self.assertEqual(context, expected, (context, expected))

    def test_post_edit_form_for_guest(self):
        """Тестируем форму редактирования записи для гостя."""
        posts_count = Post.objects.count()
        response = self.guest.post(
            self.POST_EDIT_URL,
            data=self.upload_data,
            follow=True
        )
        self.assertRedirects(
            response, AUTH_REDIRECT_URL
            + self.POST_EDIT_URL
        )
        tested_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, AUTH_REDIRECT_URL
                             + self.POST_EDIT_URL)
        contexts = {
            Post.objects.count(): posts_count,
            tested_post.text: self.post.text,
            tested_post.author: self.post.author,
            tested_post.group: self.post.group,
            response.status_code: 200
        }
        for context, expected in contexts.items():
            self.assertEqual(context, expected, (context, expected))

    def test_post_edit_form_for_another_user(self):
        """Тестируем форму редактирования записи для неавтора."""
        posts_count = Post.objects.count()
        response = self.not_author.post(
            self.POST_EDIT_URL,
            data=self.upload_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_VIEW_URL)
        post = response.context['post']
        contexts = {
            Post.objects.count(): posts_count,
            post.group: self.post.group,
            post.text: self.post.text,
            post.author: self.post.author,
            response.status_code: 200
        }
        for context, expected in contexts.items():
            self.assertEqual(context, expected, (context, expected))

    def test_post_edit_form_for_author(self):
        """Тестируем форму редактирования записи для автора."""
        posts_count = Post.objects.count()
        self.upload_data['image'] = SimpleUploadedFile(
            name='edit_form_image.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        response = self.author.post(
            self.POST_EDIT_URL,
            data=self.upload_data,
            follow=True
        )
        post = response.context['post']
        contexts = {
            Post.objects.count(): posts_count,
            post.text: self.upload_data['text'],
            post.group.id: self.upload_data['group'],
            post.author: self.post.author,
            post.image.name: 'posts/' + self.upload_data['image'].name,
            response.status_code: 200,
        }
        for context, expected in contexts.items():
            self.assertEqual(context, expected, (context, expected))

    def test_comment_form_for_guest(self):
        """Тестируем форму добавления комментария для гостя."""
        primary_comments = list(Comment.objects.all())
        comments_count = Comment.objects.count()
        response = self.guest.post(
            self.COMMENT_URL,
            data=self.comment_data,
            follow=True
        )
        self.assertRedirects(response,
                             AUTH_REDIRECT_URL + self.COMMENT_URL)
        self.assertEqual(set(Comment.objects.all()), set(primary_comments))
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertEqual(response.status_code, 200)

    def test_comment_form_for_user(self):
        """Тестируем форму добавления комментария для пользователя."""
        primary_keys = [value.pk for value in Comment.objects.all()]
        response = self.author.post(
            self.COMMENT_URL,
            data=self.comment_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_VIEW_URL)
        keys = [value.pk for value in Comment.objects.all()
                if value.pk not in primary_keys]
        self.assertEqual(len(keys), 1)
        comment = Comment.objects.get(id=keys[0])
        contexts = {
            comment.author: self.author_user,
            comment.text: self.comment_data['text'],
            response.status_code: 200,
        }
        for context, expected in contexts.items():
            self.assertEqual(context, expected, (context, expected))
