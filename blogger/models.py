from datetime import timedelta
from uuid import uuid4

import jwt as jwt
from django.utils.datetime_safe import datetime
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework import serializers
from django.utils.translation import gettext as _

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class CustomUser(AbstractUser):
    bio = models.TextField(
        "User bio",
        max_length=400,
        null=True,
        blank=True,
        default=''
    )

    SEX_CHOICES = (
        ('F', 'Female',),
        ('M', 'Male',),
        ('U', 'Unsure',),
    )
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
    )

    birth_date = models.DateField(
        "Birth Date",
        null=True,
        blank=True
    )

    # (lon, lat)
    location = models.CharField(
        "location coordinates",
        max_length=20,
        null=True,
        default="",
        blank=True
    )

    rating = models.IntegerField(
        "rating",
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ],
        default="0"
    )

    show_in_search_results = models.TextField(
        "show in search results",
        max_length=400,
        null=True,
        blank=True,
        default=""
    )

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def set_show_in_search_results(self, x):
        if x:
            self.show_in_search_results = ", ".join(x)
        else:
            self.show_in_search_results = ""

    def get_show_in_search_results(self):
        return self.show_in_search_results.split(', ')

    """getter and setter location"""
    def set_location(self, x, y):
        if x:
            self.location = f"({x},{y})"
        else:
            self.location = ""

    def get_location(self):
        if self.show_in_search_results and "," in self.show_in_search_results:
            x, y = self.show_in_search_results.split(',')

            return x, y
        else:
            return 0, 0


class Posts(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="author"
    )

    title = models.CharField("Title", max_length=150)

    text = models.TextField(
        "Post description",
        null=False,
        blank=False,
        max_length=1000
    )

    is_active = models.BooleanField("Post is active", default=True)

    created = models.DateTimeField("Create DTime", auto_now_add=True)
    updated = models.DateTimeField("Update DTime", auto_now=True)


class PostEditHistory(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="editauthor"
    )

    post = models.ForeignKey(
        Posts,
        on_delete=models.PROTECT,
        related_name="post"
    )

    text = models.TextField(
        "Change description",
        null=False,
        blank=False,
        max_length=2000
    )

    timestamp = models.DateTimeField("Edit DTime",  auto_now_add=True)


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = CustomUser.objects.create(
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            birth_date=validated_data['birth_date'],
            sex=validated_data['sex'],
            bio=validated_data['bio'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = CustomUser

        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "birth_date",
            "sex",
            'bio'
        )


class PostsSerializer(serializers.ModelSerializer):

    title = serializers.CharField(max_length=150)

    text = serializers.CharField(
        max_length=1000
    )
    is_active = serializers.BooleanField()

    class Meta:
        model = Posts
        fields = (
            "id",
            "author",
            "title",
            "text",
            "is_active",
            "created",
            "updated"
        )
        read_only_fields = ('author',)


class PostEditHistorySerializer(serializers.ModelSerializer):

    text = serializers.CharField(
        max_length=2000
    )

    class Meta:
        model = PostEditHistory
        fields = (
            "id",
            "author",
            "post",
            "text",
            "timestamp",
        )
        read_only_fields = ('author', "post")
