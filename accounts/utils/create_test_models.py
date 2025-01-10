from datetime import datetime

from mail.models import Company, Recipient, EmailFollowup


def test_models(request, object):
    company = Company.objects.create(user=request.user, name="Test")
    recipient = Recipient.objects.create(
        user=request.user,
        company=company,
        first_name="Test",
        last_name="Test",
        email=object.login
    )
    email_followup = EmailFollowup.objects.create(
        user=request.user,
        recipient=recipient,
        company=company,
        quantity=1,
        subject="Test",
        date_to_send=datetime.now(),
        original_text="Test email verification email",
        improved_text="Test email verification email",
        status="TO SEND"
    )
    return company, recipient, email_followup
