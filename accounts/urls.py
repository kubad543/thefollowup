from django.urls import path
from django.contrib.auth import views as auth_views
from .views import logout_user, dashboard, activate_account, RegisterView, ChangePasswordView, ResetPasswordView, SMTPSettingsView, profile_view, pipeline_details, register_done, stop_pipeline, article_details, delete_pipeline


urlpatterns = [
    path('logout/', logout_user, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    path('register/', RegisterView.as_view(), name='register'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('profile/', profile_view, name='profile'),
    path('', dashboard, name='main'),
    path('pipeline/<int:pipeline_id>/', pipeline_details, name='pipeline'),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
    path('settings-smtp/', SMTPSettingsView.as_view(), name='user-smtp'),
    path('register_done/', register_done, name='register_done'),
     path('pipeline/stop/<int:pipeline_id>/', stop_pipeline, name='stop_pipeline'),
     path('article/<int:id>/', article_details, name='article_details'),
     path('pipeline/delete/<int:pipeline_id>/', delete_pipeline, name='delete_pipeline'),
]