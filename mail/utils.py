from django.conf import settings
from openai import OpenAI


def generate_improved_content(org_message, previous_messages, subject, recipient_data, sender_data, language, followup_no=None):
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )

    prompt = ''
    if org_message == True:
        prompt = "Based on the email provided below, please write a new email in a natural and friendly manner. New email should be at least 5 sentences long. It should be better version of the email provided below. \n"
        prompt += "Sender: " + sender_data.name + " " + sender_data.surname + ", company: " + sender_data.company + " \n"
        prompt += "Recipient: " + recipient_data.first_name + " " + recipient_data.last_name + ", company: " + recipient_data.company.name + " \n"
        prompt += "Language of your email: " + language + " \n"
        prompt += "Subject: " + subject + " \n"
        prompt += "Do not add subject or any other information. Do not add signature or sender's first, last name or company's name after the greetings. Just plain email. \n"
        prompt += "Original email (that should be written better) for reference: " + previous_messages[0]
    else:
        prompt = "Based on the emails provided below, please write a new followup email in a natural and friendly manner. New email should be at least 5 sentences long. \n"
        prompt += "Sender: " + sender_data.name + " " + sender_data.surname + ", company: " + sender_data.company + " \n"
        prompt += "Recipient: " + recipient_data.first_name + " " + recipient_data.last_name + ", company: " + recipient_data.company.name + " \n"
        prompt += "Language of your email: " + language + " \n"
        prompt += "Subject: " + subject + " \n"
        prompt += "This is a followup number " + str(followup_no) + " \n"
        prompt += "Do not add subject or any other information. Do not add signature or sender's first, last name or company's name after the greetings. Just plain email. \n"
        prompt += "Original email (to which we are writing followup) for reference: " + previous_messages[0]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    improved_text = response.choices[0].message.content
    improved_text += "\n_\n"
    improved_text += sender_data.name + " " + sender_data.surname + " \n"
    improved_text += sender_data.company

    return improved_text


def generate_improved_content_for_several_companies(org_message, previous_messages, subject, sender_data, language, followup_no=None):
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )

    prompt = ''
    if org_message == True:
        prompt = "Based on the email provided below, please write a new email in a natural and friendly manner. New email should be at least 5 sentences long. It should be better version of the email provided below. \n"
        prompt += "Sender: " + sender_data.name + " " + sender_data.surname + ", company: " + sender_data.company + " \n"
        prompt += "Language of your email: " + language + " \n"
        prompt += "Subject: " + subject + " \n"
        prompt += "Do not add subject or any other information. Do not add signature or sender's first, last name or company's name after the greetings. Just plain email. \n"
        prompt += "Original email (that should be written better) for reference: " + previous_messages[0]
    else:
        prompt = "Based on the emails provided below, please write a new followup email in a natural and friendly manner. New email should be at least 5 sentences long. \n"
        prompt += "Sender: " + sender_data.name + " " + sender_data.surname + ", company: " + sender_data.company + " \n"
        prompt += "Language of your email: " + language + " \n"
        prompt += "Subject: " + subject + " \n"
        prompt += "This is a followup number " + str(followup_no) + " \n"
        prompt += "Do not add subject or any other information. Do not add signature or sender's first, last name or company's name after the greetings. Just plain email. \n"
        prompt += "Original email (to which we are writing followup) for reference: " + previous_messages[0]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    improved_text = response.choices[0].message.content

    return improved_text