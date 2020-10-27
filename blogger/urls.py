from django.conf.urls import url
from django.urls import path

from blogger.views import (
    CreatePostView,
    CreateUserView,
    PostView,
    UsersProfileView,
    PostEditView,
    InfoView
)

urlpatterns = [
    path('signup/', CreateUserView.as_view()),
    path('post/',CreatePostView.as_view()),
    path('post/edit/<str:pk>/', PostEditView.as_view()),
    path('post/<str:pk>/',PostView.as_view()),

    path('user/',UsersProfileView.as_view()),
    path('',InfoView.as_view())
]
