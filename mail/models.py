from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import gettext_lazy as _


class BaseModel(models.Model):
    """
    Base model to define common fields.
    """
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name=_('Data utworzenia'))
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name=_('Data ostatniej zmiany'))

    class Meta:
        abstract = True


class Company(BaseModel):
    """
    Model representing a company.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=255,
                            verbose_name=_('Nazwa'))
    url = models.URLField(verbose_name=_('Strona internetowa'), blank=True, null=True)

    def __str__(self):
        return self.name


class Recipient(BaseModel):
    """
    Model representing a recipient.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_recipients')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_recipients')
    first_name = models.CharField(max_length=50, verbose_name=_('Imię'))
    last_name = models.CharField(max_length=50, verbose_name=_('Nazwisko'))
    email = models.EmailField(verbose_name=_('Email'))

    def __str__(self):
        return self.first_name + ' ' + self.last_name + ' <' + self.email + '>'

class Pipeline(BaseModel):
    """
    Model representing a pipeline.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_pipelines')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='recipient_pipelines')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_pipelines')
    language = models.CharField(max_length=2, choices=(('pl', 'Polish'), ('en', 'English')),
                                verbose_name=_('Language'))
    status = models.CharField(max_length=10, choices=(('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('STOPPED', 'Stopped')),
                              verbose_name=_('Status'))

    def __str__(self):
        return self.recipient.first_name + ' ' + self.recipient.last_name + ' (' + str(self.company) + ') [' + self.language + ']'

class EmailFollowup(BaseModel):
    """
    Model representing an email follow-up.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_email_followups')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='recipient_email_followups')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_email_followups')
    initial_message = models.BooleanField(default=False, verbose_name=_('First message'))
    quantity = models.IntegerField(validators=[MinValueValidator(1)], default=0)
    subject = models.CharField(max_length=255, verbose_name=_('Subject'))
    date_to_send = models.DateTimeField(verbose_name=_('Data wysłania'), null=True, blank=True)
    original_text = models.TextField(verbose_name=_('Original message'))
    improved_text = models.TextField(blank=True, null=True,
                                     verbose_name=('Improved message'))  # improved text after AI, can be empty
    status = models.CharField(max_length=10, choices=(('TO SEND', 'To Send'), ('SENT', 'Sent')),
                              verbose_name=_('Status'))
    bcc_1 = models.EmailField(max_length=50, null=True, blank=True,
                               verbose_name='BCC address no 1')
    bcc_2 = models.EmailField(max_length=50, null=True, blank=True,
                               verbose_name='BCC address no 2')

    def __str__(self):
        return self.recipient.first_name + ' ' + self.recipient.last_name + ' (' + str(self.company) + ') '

class Followup(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.ForeignKey(EmailFollowup, on_delete=models.CASCADE)
    number = models.IntegerField(validators=[MinValueValidator(1)])
    date_to_send = models.DateTimeField(verbose_name=_('Data wysłania'))
    improved_text = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=(
        ('TO SEND', 'To Send'), ('SENT', 'Sent')), verbose_name=_('Status'))

    def __str__(self):
        return f'{self.user} to {self.email.recipient.first_name} ({self.email.company}) - followup no. {self.number}'
