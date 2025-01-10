from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser
from django import forms

from .models import UserSmtp


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'surname', 'company', 'bcc_1', 'bcc_2']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['surname'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['company'].widget.attrs['placeholder'] = 'Enter company name'

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            name = self.fields['name']
        return name

    def clean_surname(self):
        surname = self.cleaned_data.get('surname')
        if not surname:
            surname = self.fields['surname']
        return surname

    def clean_company(self):
        company = self.cleaned_data.get('company')
        if not company:
            company = self.fields['company']
        return company




class SMTPSettingsForm(forms.ModelForm):

    class Meta:
        model = UserSmtp
        exclude = ['user']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super(SMTPSettingsForm, self).__init__(*args, **kwargs)
        # if self.instance and self.instance.pk:
#             self.fields['password'].widget.attrs['value'] = self.instance.decrypt_password()

class ChangePasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(self.user, *args, **kwargs)
