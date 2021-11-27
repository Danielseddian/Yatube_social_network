from django.test import TestCase
from django.urls import reverse

from posts.models import Post, User


class TestRoutes(TestCase):

    def test_matching_names_of_urls(self):
        """Проверяем, что имена правильно реверсируются в url."""
        author = User.objects.create(username='Pushkin')
        group_slug = 'poet'
        post = Post.objects.create(text='Тестовый текст',
                                   author=author)
        routes = {
            reverse('posts:new_post'): '/new/',
            reverse('posts:index'): '/',
            reverse('posts:follow_index'): '/follow/',
            reverse('posts:profile', args=[
                author.username
            ]): f'/{author.username}/',
            reverse('posts:post_view', args=[
                author.username, post.id
            ]): f'/{author.username}/{post.id}/',
            reverse('posts:group_posts', args=[
                group_slug
            ]): f'/group/{group_slug}/',
            reverse('posts:post_edit', args=[
                author.username, post.id
            ]): f'/{author.username}/{post.id}/edit/',
            reverse('posts:add_comment', args=[
                author.username, post.id
            ]): f'/{author.username}/{post.id}/comment/',
            reverse('posts:profile_unfollow', args=[
                author.username
            ]): f'/{author.username}/unfollow/',
            reverse('posts:profile_follow', args=[
                author.username
            ]): f'/{author.username}/follow/',
            reverse('posts:follow_index'): '/follow/',
        }
        for url, route in routes.items():
            self.assertEqual(url, route)
