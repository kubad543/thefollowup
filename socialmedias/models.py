from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import gettext_lazy as _

from mail.models import BaseModel


class ArticlesData(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    language = models.CharField(max_length=7, choices=(('POLISH', 'Polish'), ('ENGLISH', 'English')),
                                verbose_name=_('Język'))

    def __str__(self):
        return f'{self.user} - {self.text[:20] + "..." if len(self.text) > 20 else self.text}'


class PostArticle(BaseModel):
    PLATFORM_CHOICES = [
        ('LINKEDIN', 'LinkedIn'),
        ('TWITTER', 'Twitter'),
        ('FACEBOOK', 'Facebook'),
        ('INSTAGRAM', 'Instagram'),
        ('YOUTUBE', 'YouTube'),
    ]
    article = models.ForeignKey(ArticlesData, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    limit_words = models.IntegerField(validators=[MinValueValidator(1)])
    platform = models.CharField(max_length=9, choices=PLATFORM_CHOICES)
    date_publish = models.DateField()

    def __str__(self):
        return f'{self.article} - {self.platform}'
