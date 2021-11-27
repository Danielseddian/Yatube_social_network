from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """Тест статических страниц about:author и about:tech"""
        urls = ['about:author', 'about:tech']
        for url in urls:
            response = self.guest_client.get(reverse(url))
            self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """Тест шаблонов для about:author и about:tech"""
        urls_and_templates = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html'
        }
        for url, template in urls_and_templates.items():
            response = self.guest_client.get(reverse(url))
            self.assertTemplateUsed(response, template)
