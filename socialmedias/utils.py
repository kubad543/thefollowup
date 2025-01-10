from django.conf import settings
from openai import OpenAI


def generate_improved_content(org_message, previous_messages, language, limit_words, followup_no=None):
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
    )

    prompt = ''
    if org_message == True:
        prompt = "Based on the post provided below, please write a new post in a natural and friendly manner. New post should be at least 5 sentences long. It should be better version of the post provided below. \n"
        prompt += "Language: " + language + " \n"
        prompt += "Do not add subject or any other information. Do not add signature or sender's first, last name or company's name after the greetings. Just plain post. \n"
        prompt += "Original post (that should be written better) for reference: " + previous_messages[0] + '.\n'
        prompt += f"This post should contain a maximum of this many characters {limit_words}." + "\n"
    else:
        prompt = "Based on the posts provided below, please write a new posts in a natural and friendly manner. New post should be at least 5 sentences long. \n"
        prompt += "Language: " + language + " \n"
        prompt += "This is a followup number " + str(followup_no) + " \n"
        prompt += "Do not add subject or any other information. Do not add signature or sender's first, last name or company's name after the greetings. Just plain post. \n"
        prompt += "Original post (to which we are writing post) for reference: " + previous_messages[-1] + '.\n'
        prompt += f"This post should contain a maximum of this many characters {limit_words}." + "\n"


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