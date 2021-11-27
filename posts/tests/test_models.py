from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User


class PostsModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='Pushkin')
        another_user = User.objects.create_user(username='Block')
        group = Group.objects.create(title='Poet', slug='poet')
        cls.post = Post.objects.create(
            text='А' * 1000,
            author=author,
            group=group
        )
        cls.comment = Comment.objects.create(post=cls.post,
                                             author=another_user,
                                             text='Тестовый комментарий')
        cls.follow = Follow.objects.create(user=another_user,
                                           author=author)

    def test_group_str(self):
        """Проверка отображаемой информации классом Group."""
        group = self.post.group
        expected_group_response = group.title
        self.assertEquals(expected_group_response, str(group))

    def test_post_str(self):
        """Проверка отображаемой информации классом Post."""
        post = self.post
        group = post.group.title
        author = post.author.username
        pub_date = post.pub_date
        text = post.text[:15]
        expected_post_response = (
            f'Группа: {group} Автор: {author} Текст: {text} Дата: {pub_date}'
        )
        self.assertEquals(expected_post_response, str(post))

    def test_comment_str(self):
        """Проверка отображаемой информации классом Comment."""
        comment = self.comment
        post = comment.post.text[:15]
        author = comment.author.username
        created = comment.created
        text = comment.text[:15]
        expected_comment_response = (
            f'Автор: {author} Комментарий: {text} Дата: {created} '
            f'В ответ на пост: {post}'
        )
        self.assertEquals(expected_comment_response, str(comment))

    def test_follow_str(self):
        """Проверка отображаемой информации классом Follow."""
        follow = self.follow
        author = follow.author.username
        user = follow.user.username
        expected_follow_response = (
            f'Пользователь: {user} Подписан на: {author}'
        )
        self.assertEquals(expected_follow_response, str(follow))
