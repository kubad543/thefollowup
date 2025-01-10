import smtplib
from datetime import datetime
from email.mime.text import MIMEText

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from django.http import Http404
from django.contrib import messages

from utils.mail_to_someone import send_mail_to_someone
from .models import UserSmtp, CustomUser
from socialmedias.models import PostArticle
from mail.models import Pipeline, Followup, EmailFollowup, Recipient, Company
from .tokens import account_activation_token
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin

from followup import settings
from .forms import ChangePasswordForm, UserProfileForm, SMTPSettingsForm, UserRegisterForm
from .utils.create_test_models import test_models
from .utils.remove_models import remove_models


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'account/register_done.html')
    else:
        return render(request, 'account/activation_invalid.html')


def logout_user(request):
    logout(request)
    return render(request, 'account/logout.html')


@login_required
def dashboard(request):
    pipelines = Pipeline.objects.filter(user=request.user).order_by('-updated_at')
    articles = PostArticle.objects.filter(article__user=request.user).order_by('-updated_at')
 
    paginator_pipelines = Paginator(pipelines, 10)
    paginator_articles = Paginator(articles, 10)
    
    page_number_pipelines = request.GET.get('page_pipelines')
    page_number_articles = request.GET.get('page_articles')
    
    page_obj_pipelines = paginator_pipelines.get_page(page_number_pipelines)
    page_obj_articles = paginator_articles.get_page(page_number_articles)
    
    custom_user, created = CustomUser.objects.get_or_create(user=request.user)
    
    return render(request, 'account/dashboard.html', {
        'page_obj_pipelines': page_obj_pipelines,
        'page_obj_articles': page_obj_articles,
        'custom_user': custom_user,
    })


@login_required
def profile_view(request):
    current_user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST,
                               instance=current_user.customuser if hasattr(current_user, 'customuser') else None)
        if form.is_valid():
            custom_user = form.save(commit=False)
            custom_user.user = current_user
            custom_user.save()
            messages.success(request, "Profile has been updated.")
            return redirect('profile')
    else:
        initial_data = {
            'name': current_user.customuser.name if hasattr(current_user, 'customuser') else None,
            'surname': current_user.customuser.surname if hasattr(current_user, 'customuser') else None,
            'company': current_user.customuser.company if hasattr(current_user, 'customuser') else None,
        }
        form = UserProfileForm(instance=current_user.customuser if hasattr(current_user, 'customuser') else None,
                               initial=initial_data)

    context = {
        'form': form,
    }

    return render(request, 'account/profile.html', context)


@login_required()
def pipeline_details(request, pipeline_id):
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
    except Http404:
        messages.error(request, "No such pipeline found.")
        return redirect('dashboard')
    custom_user = request.user.customuser 
    try:
        email_followup = get_object_or_404(EmailFollowup, recipient=pipeline.recipient)
    except Http404:
        messages.error(request, "No such pipeline found.")
        return redirect('dashboard')
    followups = []
    for i in range(email_followup.quantity):
        try:
            followup = Followup.objects.get(user=email_followup.user, email=email_followup, number=i + 1)
            followups.append(followup)
        except Followup.DoesNotExist:
            followups.append(None)

    if pipeline.user == request.user:
        return render(request, 'account/pipeline_details.html', {
            'pipeline': pipeline,
            'custom_user': custom_user,
            'email_followups': email_followup,
            'followups': followups,
        })
    else:
        return redirect('dashboard')
    
@login_required()
def article_details(request, id):
    post_article = get_object_or_404(PostArticle, id=id)
    article = post_article.article
    posts = PostArticle.objects.filter(article=article)
    custom_user = request.user.customuser
    
    if article.user == request.user:
        return render(request, 'account/article_details.html', {
            'article': article,
            'posts': posts,
            'custom_user': custom_user,
        })
    else:
        return redirect('dashboard')


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'account/password_reset.html'
    email_template_name = 'account/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('account_login')


class RegisterView(CreateView):
    template_name = 'account/register.html'
    success_url = reverse_lazy('account_login')
    form_class = UserRegisterForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.username = form.cleaned_data['email']
        try:
            user.save()
        except IntegrityError:
            messages.error(self.request, 'This email address is already registered.')
            return self.form_invalid(form)
        messages.success(self.request, 'Registration was successful. You must activate your account via email.')

        token = account_activation_token.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        subject = "Registration Confirmed"
        message = "Thank you for registering. Please confirm your email."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        link = self.request.build_absolute_uri(reverse('activate_account', kwargs={'uidb64': uidb64, 'token': token}))
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
            html_message=render_to_string(
                'account/email/mail_confirm.html',
                {'link': link, 'user': user})
        )
        return super().form_valid(form)


class SMTPSettingsView(LoginRequiredMixin, UpdateView):
    model = UserSmtp
    form_class = SMTPSettingsForm
    template_name = 'account/edit_smtp_settings.html'
    success_url = reverse_lazy('user-smtp')

    def get_object(self, queryset=None):
        try:
            return UserSmtp.objects.get(user=self.request.user)
        except UserSmtp.DoesNotExist:
            smtp_object = UserSmtp(user=self.request.user)
            #smtp_object.save()
            return smtp_object

    def form_valid(self, form):
        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.user = self.request.user
                plain_passwd = self.object.password
                self.object.save()

                company, recipient, email_followup = test_models(self.request, self.object)
                email_sent = send_mail_to_someone(email_followup=email_followup, user=self.request.user)
                if not email_sent:
                    messages.error(self.request, "Unknown error while sending test email. SMTP authentication failed.")
                    return self.form_invalid(form)

                remove_models(company, recipient, email_followup)

                self.object.password = plain_passwd
                response = super().form_valid(form)
                messages.success(self.request, 'SMTP settings updated successfully. A test email has been sent.')

                return response
                
        except smtplib.SMTPAuthenticationError as e:
            messages.error(self.request,
                           f'SMTP authentication failed: {e}')
            remove_models(company, recipient, email_followup)
            return self.form_invalid(form)
        except Exception as e:
            print(f"Unexpected {e=}, {type(e)=}")
            messages.error(self.request,
                           f'Error sending test email')
            remove_models(company, recipient, email_followup)
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with the form. Please correct the errors below.')
        return super().form_invalid(form)


class ChangePasswordView(PasswordChangeView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('change-password')
    template_name = 'account/change_password.html'

    def form_valid(self, form):
        messages.success(self.request, "Password has been successfully changed. ")
        return super().form_valid(form)


def register_done(request):
    return render(request, 'account/register_done.html')


@login_required
def stop_pipeline(request, pipeline_id):
    if request.method == "POST":
        pipeline = get_object_or_404(Pipeline, id=pipeline_id, user=request.user)
        if pipeline.status == 'ACTIVE':
            pipeline.status = 'STOPPED'
            messages.success(request, "Pipeline has been stopped.")
        else:
            pipeline.status = 'STOPPED'
            messages.success(request, "Pipeline has been stopped.")
        pipeline.save()
        return redirect('pipeline', pipeline_id=pipeline_id)

    
@login_required
def delete_pipeline(request, pipeline_id):
    pipeline = get_object_or_404(Pipeline, id=pipeline_id, user=request.user)
    email_followup = get_object_or_404(EmailFollowup, recipient=pipeline.recipient) 

    Followup.objects.filter(user=email_followup.user, email=email_followup).delete()
    email_followup.delete()
    pipeline.delete()
    messages.success(request, "Pipeline has been deleted.")
    return redirect('dashboard')
