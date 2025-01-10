from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    def send_mail(self, template_prefix, email, context):
        # Add your custom link to the context
        # context['LOGO_LINK'] = settings.LOGO_LINK
        super().send_mail(template_prefix, email, context)

    def is_open_for_signup(self, request):
        """
        The function disables the possibility of registering on the website
        :param request: a request person cannot register
        :return: True
        """
        return True
