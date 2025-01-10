from django.urls import path
from .views import PostDataForm, PostArticleCreateView, GeneratorTextView

urlpatterns = [
    path('', PostDataForm.as_view(), name='post-data'),
    path('<int:pk>/', PostArticleCreateView.as_view(), name='create-post-article'),
    path('list-mails/<int:pk>/', GeneratorTextView.as_view(), name='generate-text-article'),

]