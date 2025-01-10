# Generated by Django 5.0.6 on 2024-09-09 14:07

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticlesData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Data ostatniej zmiany')),
                ('text', models.TextField()),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('language', models.CharField(choices=[('POLISH', 'Polish'), ('ENGLISH', 'English')], max_length=7, verbose_name='Język')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PostArticle',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data utworzenia')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Data ostatniej zmiany')),
                ('text', models.TextField(blank=True, null=True)),
                ('limit_words', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('platform', models.CharField(choices=[('LINKEDIN', 'LinkedIn'), ('TWITTER', 'Twitter'), ('TWITTER+', 'Twitter+'), ('FACEBOOK', 'Facebook'), ('INSTAGRAM', 'Instagram'), ('YOUTUBE', 'YouTube')], max_length=9)),
                ('date_publish', models.DateField(blank=True, null=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socialmedias.articlesdata')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
