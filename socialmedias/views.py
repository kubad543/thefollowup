from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, CreateView

from accounts.models import CustomUser
from .forms import ArticlesDataForm, PostArticleForm
from .models import ArticlesData, PostArticle
from .utils import generate_improved_content


class PostDataForm(FormView):
    template_name = 'socialmedias/post-data.html'
    form_class = ArticlesDataForm

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('create-post-article', kwargs={'pk': self.object.pk})


class PostArticleCreateView(View):
    template_name = 'socialmedias/post-article-create.html'
    PLATFORM_LIMITS = {
        'LINKEDIN': 1300,
        'TWITTER': 280,
        'FACEBOOK': 63206,
        'INSTAGRAM': 2200,
        'YOUTUBE': 5000
    }

    def get(self, request, pk, *args, **kwargs):
        article_data = ArticlesData.objects.filter(pk=pk).first()
        post_article = PostArticle.objects.filter(article=article_data)
        if post_article.exists():
            return redirect('generate-text-article', pk=pk)
        article = self.get_article()
        forms = [PostArticleForm(prefix=str(i)) for i in range(article.quantity)]
        return self.render_to_response({'forms': forms, 'article': article, 'range': range(1, article.quantity + 1)})

    def post(self, request, *args, **kwargs):
        article = self.get_article()
        forms = [PostArticleForm(request.POST, prefix=str(i)) for i in range(article.quantity)]
        dates = request.POST.getlist(f'date')
        platforms = request.POST.getlist(f'platform')
        if len(dates) == len(platforms):
            for date, platform in zip(dates, platforms):
                post_article = PostArticle(article=article, platform=platform, date_publish=date)
                if platform in self.PLATFORM_LIMITS:
                    post_article.limit_words = self.PLATFORM_LIMITS[platform]
                post_article.save()
            messages.success(request, 'Posts have been successfully created.')
            return redirect(reverse('generate-text-article', kwargs={'pk': article.pk}))

        else:
            messages.error(request, 'An error occurred while creating posts.')
        return self.render_to_response({'forms': forms, 'article': article, 'range': range(1, article.quantity + 1)})

    def get_article(self):
        article_id = self.kwargs.get('pk')
        return get_object_or_404(ArticlesData, pk=article_id, user=self.request.user)

    def render_to_response(self, context):
        return TemplateResponse(self.request, self.template_name, context)


class GeneratorTextView(View):

    def get(self, request, pk):
        article_data = get_object_or_404(ArticlesData, pk=pk)
        if article_data.user != request.user:
            return redirect('dashboard')
        custom_user = get_object_or_404(CustomUser, user=article_data.user)
        if not custom_user:
            return redirect('dashboard')
        articles = PostArticle.objects.filter(article=article_data)
        if not articles.exists():
            return redirect('create-post-article',  pk=pk)

        previous_messages = [article_data.text]
        followup_contents = []
        num = 0

        for idx, article in enumerate(articles):
            idx_n = idx + 1
            if not article.text:
                if num == 0:
                    new_message = generate_improved_content(True, previous_messages, article_data.language,
                                                            article.limit_words, idx_n)
                    num += 1
                else:
                    new_message = generate_improved_content(False, previous_messages, article_data.language,
                                                            article.limit_words, idx_n)

                followup_contents.append(new_message)
                previous_messages.append(new_message)
            else:
                followup_contents.append(article.text)
        return render(
            request,
            'socialmedias/list-generated-post.html',
            {
                'article_contents': followup_contents,
                'quantity': range(article_data.quantity)
            }
        )

    def post(self, request, pk):
        article_data = get_object_or_404(ArticlesData, pk=pk)
        if article_data.user != request.user:
            return redirect('dashboard')
        custom_user = get_object_or_404(CustomUser, user=article_data.user)
        if not custom_user:
            return redirect('dashboard')
        post_articles = PostArticle.objects.filter(article=article_data)
        quantity = min(len(post_articles), int(request.POST.get('quantity', 0)))

        for i, post_article in enumerate(post_articles[:quantity], start=1):
            followup_content = request.POST.get(f'article_content_{i}')
            if followup_content:
                post_article.text = followup_content
                post_article.save()

        messages.success(request, 'Posts have been successfully updated.')
        return redirect('dashboard')

