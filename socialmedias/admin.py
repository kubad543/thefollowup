from django.contrib import admin

from .models import PostArticle, ArticlesData


@admin.register(ArticlesData)
class ArticlesDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'quantity', 'language')
    list_filter = ['language', 'user']


@admin.register(PostArticle)
class PostArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'article', 'short_text', 'limit_words', 'platform', 'date_publish')
    list_filter = ['article', 'platform']

    def short_text(self, obj):
        if obj.text:
            return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
        return None

    short_text.short_description = 'Text'


