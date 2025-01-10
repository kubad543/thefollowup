import re
from cryptography.fernet import Fernet, InvalidToken
import base64

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User, AbstractUser, Permission, Group
from django.utils.text import gettext_lazy as _


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name='customuser')
    name = models.CharField(max_length=50, verbose_name='First name',
                            validators=[
                                RegexValidator(r'^[A-Za-z]{3,}$',
                                               _('The name must consist of at least 3 letters.'),
                                               flags=re.I)])
    surname = models.CharField(max_length=50, verbose_name='Last name',
                               validators=[
                                   RegexValidator(r'^[A-Za-z]{3,}$',
                                                  _('Surname must consist of at least 3 letters.'),
                                                  flags=re.I)])
    phone = models.CharField(max_length=9, null=True, verbose_name='Phone',
                             validators=[RegexValidator(r'^[0-9]{9}$',
                                                        _('Phone number must consist of at least 9 digits.'),
                                                        flags=re.I)])
    date_joined = models.DateField(auto_now_add=True, editable=False,
                                   verbose_name='Date joined')
    date_change = models.DateField(auto_now=True,
                                   verbose_name='Date modified')
    company = models.CharField(max_length=50, null=True,
                               verbose_name='Company name')
    bcc_1 = models.EmailField(max_length=50, null=True, blank=True,
                               verbose_name='BCC address no 1')
    bcc_2 = models.EmailField(max_length=50, null=True, blank=True,
                               verbose_name='BCC address no 2')


class UserSmtp(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=3)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    tls = models.BooleanField(default=False)

    def __str__(self):
        return f"SMTP Settings for {self.user.username}"

    def save(self, *args, **kwargs):
        self.password = self.encrypt_password(self.password)
        super().save(*args, **kwargs)

    def encrypt_password(self, raw_password):
        cipher_suite = Fernet(settings.FERNET_KEY.encode())
        encrypted_password = cipher_suite.encrypt(raw_password.encode())
        return encrypted_password.decode()

    def decrypt_password(self):
        cipher_suite = Fernet(settings.FERNET_KEY.encode())
        try:
            decrypted_password = cipher_suite.decrypt(self.password.encode())
            return decrypted_password.decode()
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            print('Problem with sending / decrypted password error')
            return None

    def check_password(self, raw_password):
        try:
            decrypted_password = self.decrypt_password()
            return raw_password == decrypted_password
        except Exception:
            return False

    def password_needs_encrypting(self):
        try:
            self.decrypt_password()
            return False
        except Exception:
            return True