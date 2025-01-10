from datetime import datetime

from django.conf import settings
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import FormView

from accounts.models import CustomUser, UserSmtp
from utils.mail_to_someone import send_mail_to_someone
from .forms import CreateFollowUpForm, EmailFollowupForm, PipelineCreateForm
from .models import EmailFollowup, Pipeline, Followup, Company, Recipient
from .utils import generate_improved_content, \
    generate_improved_content_for_several_companies


class RecipientView(FormView):
    template_name = 'mail/recipient_form.html'
    form_class = CreateFollowUpForm

    def dispatch(self, request, *args, **kwargs):
        try:
            custom_user = CustomUser.objects.get(user=request.user)
            if not custom_user.surname or not custom_user.company or not custom_user.name:
                messages.error(request, 'You need to configure Profile.')
                return redirect(reverse('profile'))
        except CustomUser.DoesNotExist:
            messages.error(request, 'You need to configure Profile.')
            return redirect(reverse('profile'))

        try:
            UserSmtp.objects.get(user=request.user)
        except UserSmtp.DoesNotExist:
            messages.error(request,'You need to configure SMTP settings before proceeding.')
            return redirect(reverse('user-smtp'))

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return { 'bcc_1': self.request.user.customuser.bcc_1, 'bcc_2': self.request.user.customuser.bcc_2 }

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email_follow_up = form.save(request)
            return redirect('email-followup-update', pk=email_follow_up.id)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class EmailFollowupUpdateView(View):
    model = EmailFollowup
    form_class = EmailFollowupForm
    template_name = 'mail/emailfollowup_form.html'

    def get(self, request, pk):
        email_followup = get_object_or_404(EmailFollowup, pk=pk)
        if email_followup.user != request.user:
            return redirect('dashboard')
        form = self.form_class(instance=email_followup)
        return render(request, 'mail/emailfollowup_form.html',
                      {'form': form, 'email_followup': email_followup})

    def post(self, request, pk):
        email_followup = get_object_or_404(EmailFollowup, pk=pk)
        if email_followup.user != request.user:
            return redirect('dashboard')
        form = self.form_class(request.POST, instance=email_followup)
        if form.is_valid():
            form.save()
            return redirect(reverse('followup_form', args=[pk]))
        return render(request, 'mail/emailfollowup_form.html',
                      {'form': form, 'email_followup': email_followup})


class FollowupView(LoginRequiredMixin, View):

    def get(self, request, pk):
        email_followup = get_object_or_404(EmailFollowup, pk=pk)
        if email_followup.user != request.user:
            return redirect('dashboard')
        custom_user = get_object_or_404(CustomUser, user=email_followup.user)
        previous_messages = [email_followup.improved_text]
        followup_contents = []
        pipeline = get_object_or_404(Pipeline,
                                     recipient=email_followup.recipient)
        for i in range(email_followup.quantity):
            new_message = generate_improved_content(False, previous_messages,
                                                    email_followup.subject,
                                                    email_followup.recipient,
                                                    email_followup.user.customuser,
                                                    pipeline.language, i + 1)
            followup_contents.append(new_message)
            previous_messages.append(new_message)
        return render(request, 'mail/followup_form.html',
                      {'quantity': range(email_followup.quantity),
                       'followup_contents': followup_contents})

    def post(self, request, pk):
        email_followup = get_object_or_404(EmailFollowup, pk=pk)
        if email_followup.user != request.user:
            return redirect('dashboard')
        pipeline = get_object_or_404(Pipeline,
                                     recipient=email_followup.recipient)
        pipeline.status = 'ACTIVE'
        pipeline.save()

        for i in range(1, int(request.POST.get('quantity', 0)) + 1):
            followup_content = request.POST.get(f'followup_content_{i}')
            date_value = request.POST.getlist(f'date_{i}')
            if date_value and followup_content:
                followup = Followup.objects.create(
                    user=email_followup.user,
                    email=email_followup,
                    number=i,
                    date_to_send=date_value[0],
                    improved_text=followup_content,
                    status='TO SEND'
                )
                followup.save()
        send_mail_to_someone(email_followup, request.user)
        email_followup.date_to_send = datetime.now()
        email_followup.status = 'SENT'
        email_followup.save()

        messages.success(request, "Mail has been sent.")

        return redirect('dashboard')


class PipelineCreateView(LoginRequiredMixin, View):
    form_class = PipelineCreateForm
    template_name = 'mail/create-pipeline.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            recipients_data = form.cleaned_data['recipients']
            language = form.cleaned_data['language']
            quantity = form.cleaned_data['quantity']
            subject = form.cleaned_data['subject']
            text = form.cleaned_data['text']

            recipients = []
            for line in recipients_data.splitlines():
                parts = line.split(';')
                if len(parts) == 5:
                    first_name, last_name, email, company_name, company_url = parts
                    recipients.append({
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'company_name': company_name,
                        'company_url': company_url,
                    })
                else:
                    messages.error(request,
                                   f'Invalid recipient format: {line}')
                    return render(request, self.template_name, {'form': form})
            with transaction.atomic():
                email_followup_idx = []
                try:
                    for recipient_data in recipients:
                        company = Company.objects.create(user=request.user,
                                                         name=recipient_data[
                                                             'company_name'])
                        recipient = Recipient.objects.create(
                            user=request.user,
                            company=company,
                            first_name=recipient_data['first_name'],
                            last_name=recipient_data['last_name'],
                            email=recipient_data['email']
                        )
                        pipeline = Pipeline.objects.create(
                            user=request.user,
                            language=language,
                            company=company,
                            recipient=recipient,
                            status='DRAFT'
                        )
                        email_followup = EmailFollowup.objects.create(
                            user=request.user,
                            recipient=recipient,
                            company=company,
                            quantity=quantity,
                            subject=subject,
                            date_to_send=datetime.now(),
                            original_text=text,
                            status="TO SEND"
                        )
                        email_followup_idx.append(email_followup.id)
                    request.session['email_followup_idx'] = email_followup_idx
                    url = reverse('generate-text-to-mails')
                    return redirect(url)
                except Exception as e:
                    messages.error(request, f'An error occurred: {e}')
                    return render(request, self.template_name, {'form': form})

        return render(request, self.template_name, {'form': form})


class GenerateImprovedTextToMailsView(LoginRequiredMixin, View):
    form_class = EmailFollowupForm
    template_name = 'mail/emailfollowup_form.html'

    def get(self, request):
        email_followup_idx = request.session.get('email_followup_idx', [])
        if not email_followup_idx:
            return redirect('create-pipeline')
        email_followup = EmailFollowup.objects.filter(
            id__in=email_followup_idx).first()
        if not email_followup:
            messages.error(request, 'Email followup not found.')
            return redirect('create-pipeline')
        pipeline = Pipeline.objects.filter(
            recipient=email_followup.recipient)[0]
        if not pipeline:
            messages.error(request, 'Pipeline not found.')
            return redirect('create-pipeline')
        new_message = generate_improved_content_for_several_companies(
            True,
            [email_followup.original_text],
            email_followup.subject,
            email_followup.user.customuser,
            pipeline.language
        )
        email_followup.improved_text = new_message
        email_followup.save()
        form = self.form_class(instance=email_followup)

        return render(request, 'mail/generate_text_mail.html',
                      {'form': form, 'email_followup': email_followup})

    def post(self, request):
        email_followup_idx = request.session.get('email_followup_idx', [])
        if not email_followup_idx:
            return redirect('create-pipeline')

        email_followup = EmailFollowup.objects.filter(
            id__in=email_followup_idx)
        if not email_followup.first():
            messages.error(request, 'Email followup not found.')
            return redirect('create-pipeline')

        form = self.form_class(request.POST)
        if form.is_valid():
            for emails in email_followup:
                emails.improved_text = form.cleaned_data['improved_text']
            messages.success(request, 'Email followup updated successfully.')
            request.session['email_followup_idx'] = email_followup_idx

            return redirect('followup-mails')
        else:
            messages.error(request, 'Please correct the errors below.')

        return render(request, self.template_name,
                      {'form': form, 'email_followup': email_followup})


class FollowupMailsView(LoginRequiredMixin, View):

    def get(self, request):
        email_followup_idx = request.session.get('email_followup_idx', [])

        email_followup = get_object_or_404(EmailFollowup, pk=email_followup_idx[0])
        if email_followup.user != request.user:
            return redirect('dashboard')
        custom_user = get_object_or_404(CustomUser, user=email_followup.user)
        previous_messages = [email_followup.improved_text]
        followup_contents = []
        pipeline = get_object_or_404(Pipeline, recipient=email_followup.recipient)

        for i in range(email_followup.quantity):
            new_message = generate_improved_content_for_several_companies(
                False,
                previous_messages,
                email_followup.subject,
                email_followup.user.customuser,
                pipeline.language,
                i + 1
            )   
            followup_contents.append(new_message)
            previous_messages.append(new_message)

        return render(request, 'mail/followup_form.html', {
            'quantity': range(email_followup.quantity),
            'followup_contents': followup_contents,
            'email_followup_idx': email_followup_idx,
        })

    def post(self, request):
        email_followup_idx = request.session.get('email_followup_idx')

        email_first = get_object_or_404(EmailFollowup, pk=email_followup_idx[0])

        for j in range(len(email_followup_idx)):
            email_followup = get_object_or_404(EmailFollowup, pk=email_followup_idx[j])
            if email_followup.user != request.user:
                return redirect('dashboard')
            pipeline = get_object_or_404(Pipeline, recipient=email_followup.recipient)
            pipeline.status = 'ACTIVE'
            pipeline.save()
            email_followup.improved_text = email_first.improved_text

            for i in range(1, int(request.POST.get('quantity', 0)) + 1):
                date_value = request.POST.getlist(f'date_{i}')
                followup_content = request.POST.get(f'followup_content_{i}')
                if date_value and followup_content:
                    followup = Followup.objects.create(
                        user=email_followup.user,
                        email=email_followup,
                        number=i,
                        date_to_send=date_value[0],
                        improved_text=followup_content,
                        status='TO SEND'
                    )
                    followup.save()

            send_mail_to_someone(email_followup, request.user)
            email_followup.date_to_send = datetime.now()
            email_followup.status = 'SENT'
            email_followup.save()

        return redirect('dashboard')
