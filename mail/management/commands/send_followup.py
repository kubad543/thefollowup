import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.shortcuts import get_object_or_404

from accounts.models import UserSmtp
from mail.models import Pipeline, EmailFollowup, Followup
from utils.mail_to_someone import send_mail_to_someone


class Command(BaseCommand):
    help = 'Checks if there is any followup email to send and sends it'

    def handle(self, *args, **options):
        print('Let\'s check if there is anything to send...')
        recipient_idx = Pipeline.objects.filter(status='ACTIVE').values_list('recipient', flat=True)
        emails_idx = EmailFollowup.objects.filter(recipient_id__in=recipient_idx).values_list('id', flat=True)
        followups = Followup.objects.filter(Q(email_id__in=emails_idx) & Q(status='TO SEND')).order_by('-date_to_send')
        if not followups:
            print('There is nothing to send.')
        for followup in followups:
            print('Followup to check: ' + str(followup.id))
            if followup.status == "TO SEND" and followup.date_to_send.date() == datetime.datetime.now().date():
                print('I\'m going to send this followup...')
                send_mail_to_someone(followup.email, followup.user, followup)
                followup.status = 'SENT'
                followup.save()
                self.stdout.write(self.style.SUCCESS(f'The message has been sent to: {followup.email.recipient.company.name} {followup.email.recipient.email}'))
            else:
                self.stdout.write(self.style.ERROR(
                    f"Skipping followup ID: {followup.id}. Status: {followup.status}, Date to Send: {followup.date_to_send.date()}"))

