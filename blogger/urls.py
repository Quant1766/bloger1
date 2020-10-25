from django.conf.urls import url
from django.urls import path

from blogger.views import ListWeather

urlpatterns = [
    path('', ListWeather.as_view()),
]
