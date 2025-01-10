def remove_models(company, recipient, email_followup):
    company.delete()
    recipient.delete()
    email_followup.delete()
