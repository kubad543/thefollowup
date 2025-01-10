import openai
from django import forms
from django.core.validators import MinValueValidator
from openai import OpenAI

from accounts.models import CustomUser
from utils.get_or_none import get_or_none
from .models import Company, EmailFollowup, Recipient, Pipeline
from .utils import generate_improved_content


class CreateFollowUpForm(forms.Form):
    name = forms.CharField(max_length=255)
    surname = forms.CharField(max_length=255)
    recipient_mail = forms.EmailField()
    company_name = forms.CharField(max_length=255)
    company_url = forms.CharField(max_length=255, required=False)
    langauge_text = forms.ChoiceField(choices=(('pl', 'Polish'), ('en', 'English')))
    text_mail = forms.Textarea()
    quantity = forms.IntegerField(validators=[MinValueValidator(1)])
    subject = forms.CharField(max_length=255)
    original_text = forms.CharField(widget=forms.Textarea)
    bcc_1 = forms.EmailField(label='BCC address 1', required=False)
    bcc_2 = forms.EmailField(label='BCC address 2', required=False)

    def save(self, request):
        company = Company.objects.get_or_create(
            user=request.user,
            name=self.cleaned_data['company_name'],
            url=self.cleaned_data['company_url']
        )[0]
        recipient = Recipient.objects.create(
            user=request.user,
            first_name=self.cleaned_data['name'],
            last_name=self.cleaned_data['surname'],
            email=self.cleaned_data['recipient_mail'],
            company=company,
        )
        pipeline = Pipeline.objects.create(
            user=request.user,
            recipient=recipient,
            company=company,
            language=self.cleaned_data['langauge_text'],
            status='DRAFT',
        )
        custom_user = get_or_none(CustomUser, user=request.user)
        full_name = f'{custom_user.name} {custom_user.surname}'
        improved_text = generate_improved_content(True, [self.cleaned_data['original_text']], self.cleaned_data['subject'], recipient, custom_user, pipeline.language)
        email_follow_up = EmailFollowup.objects.create(
            user=request.user,
            recipient=recipient,
            company=company,
            initial_message=True,
            quantity=self.cleaned_data['quantity'],
            subject=self.cleaned_data['subject'],
            original_text=self.cleaned_data['original_text'],
            improved_text=improved_text,
            status='TO SEND',
            bcc_1=self.cleaned_data['bcc_1'],
            bcc_2=self.cleaned_data['bcc_2'],
        )
        email_follow_up.save()
        return email_follow_up


class EmailFollowupForm(forms.ModelForm):
    class Meta:
        model = EmailFollowup
        fields = ['improved_text']


class PipelineCreateForm(forms.Form):
    recipients = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'first name;last name;email;company name;company url\nfirst name;last name;email;company name;company url'}),
        label='Recipients (one per line)',
    )
    language = forms.ChoiceField(choices=(('pl', 'Polish'), ('en', 'English')))
    quantity = forms.IntegerField(min_value=1, label='Quantity')
    subject = forms.CharField(max_length=255, label='Subject')
    text = forms.CharField(widget=forms.Textarea, label='Text')
