from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework import serializers
from django.utils.translation import gettext as _


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.email

class Posts(models.Model):
    author = models.DecimalField(max_digits=4, decimal_places=2,null=True)
    text = models.DateTimeField("Registry DTime",null=False, blank=False, unique=True)
    created = models.DateTimeField("Registry DTime",null=False, blank=False, unique=True)
    updated = models.DateTimeField("Registry DTime",null=False, blank=False, unique=True)