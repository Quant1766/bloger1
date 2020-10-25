from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
# from django.contrib.gis.db import models as gis_models
from rest_framework import serializers
from django.utils.translation import gettext as _

from bloger import settings


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
    # location = gis_models.PointField()

    rating = models.ImageField(
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


class Posts(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="author"
    )

    image = models.ImageField(upload_to="blogpost/posts", default='')

    title = models.CharField("Title", max_length=150)

    text = models.DateTimeField(
        "Post description",
        null=False,
        blank=False,
        max_length=1000
    )

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

    text = models.DateTimeField(
        "Change description",
        null=False,
        blank=False,
        max_length=300
    )

    timestamp = models.DateTimeField("Edit DTime",  auto_now_add=True)
