# Generated by Django 2.2.11 on 2020-10-27 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogger', '0003_remove_posts_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='posts',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Post is active'),
        ),
    ]