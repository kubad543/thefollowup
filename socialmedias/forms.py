from django import forms
from django.forms import modelformset_factory

from .models import ArticlesData, PostArticle


class ArticlesDataForm(forms.ModelForm):

    class Meta:
        model = ArticlesData
        exclude = ['user']


class PostArticleForm(forms.ModelForm):
    platform = forms.ChoiceField(choices=PostArticle.PLATFORM_CHOICES, required=True, label="Platforma")

    class Meta:
        model = PostArticle
        fields = ['platform']

