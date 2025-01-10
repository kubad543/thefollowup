from django.urls import path
from .views import EmailFollowupUpdateView, RecipientView, FollowupView, \
    PipelineCreateView, GenerateImprovedTextToMailsView, FollowupMailsView

urlpatterns = [
    path('recipeint/', RecipientView.as_view(), name='email-recipeint'),
    path('emailfollowup/update/<int:pk>/', EmailFollowupUpdateView.as_view(), name='email-followup-update'),
    path('followup/<int:pk>/', FollowupView.as_view(), name='followup_form'),
    path('create-pipeline/', PipelineCreateView.as_view(),
         name='create-pipeline'),
    path('generate-text/', GenerateImprovedTextToMailsView.as_view(), name='generate-text-to-mails'),
    path('followup/mails/',FollowupMailsView.as_view(), name='followup-mails'),
]