import os

from dotenv import load_dotenv
from openai import OpenAI

# load values from the .env file if it exists
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"
TEMPERATURE = 0.5
MAX_TOKENS = 500
# limits how many previous exchanges we include in the prompt
MAX_CONTEXT_QUESTIONS = 10

INSTRUCTIONS = """You are an AI assistant that is an expert in women health and women safety.
You know about health, lifestyle, hygiene and safety.
You can provide advice on living a healthy life, being productive, dealing with anxiety and stress, preventing danger.
If you are unable to provide an answer to a question, please respond with the phrase "I'm just a health assistant, I can't help with that."
Please aim to be as helpful, creative, and friendly as possible in all of your responses.
Do not use any external URLs in your answers. Do not refer to any blogs in your answers.
Format any lists on individual lines with a dash and a space in front of each item.
"""


def get_moderation(question):
    """
    Check the question is safe to ask the model.

    Returns a list of flagged category names if the question is not safe,
    otherwise returns None.
    """
    result = client.moderations.create(input=question).results[0]
    if result.flagged:
        return [
            category
            for category, flagged in result.categories.model_dump(by_alias=True).items()
            if flagged
        ]
    return None


def get_chatbot_response(new_question, previous_questions_and_answers):
    """
    Get a chatbot answer for the new question, using recent conversation
    history as context.
    """
    flagged_categories = get_moderation(new_question)
    if flagged_categories:
        return (
            "Sorry, your question didn't pass the moderation check: "
            + ", ".join(flagged_categories)
        )

    messages = [{"role": "system", "content": INSTRUCTIONS}]
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": answer})
    messages.append({"role": "user", "content": new_question})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    answer = response.choices[0].message.content

    previous_questions_and_answers.append((new_question, answer))
    return answer


def get_chatbot(new_question):
    return get_chatbot_response(new_question, [])
