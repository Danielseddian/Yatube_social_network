from django.urls import path

from about.views import AboutAuthorView, AboutTechView

app_name = 'about'

urlpatterns = [
    path('author/',
         AboutAuthorView.as_view(template_name='about/author.html'),
         name='author'),
    path('tech/',
         AboutTechView.as_view(template_name='about/tech.html'),
         name='tech'),
]
