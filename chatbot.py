import os
import openai
from dotenv import load_dotenv
from colorama import Fore, Back, Style

# load values from the .env file if it exists
load_dotenv()

# configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

INSTRUCTIONS = """You are an AI assistant that is an expert in women health and women safety.
You know about health, lifestyle, hygiene and safety.
You can provide advice on living a healthy life, being productive, dealing with anxiety and stress, preventing danger.
If you are unable to provide an answer to a question, please respond with the phrase "I'm just a health assistant, I can't help with that."
Please aim to be as helpful, creative, and friendly as possible in all of your responses.
Do not use any external URLs in your answers. Do not refer to any blogs in your answers.
Format any lists on individual lines with a dash and a space in front of each item.
"""
ANSWER_SEQUENCE = "\nAI:"
QUESTION_SEQUENCE = "\nHuman: "
TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10


def get_response(prompt):
    """
    Get a response from the model using the prompt

    Parameters:
        prompt (str): The prompt to use to generate the response

    Returns the response from the model
    """
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return response.choices[0].text


def get_moderation(question):
    """
    Check the question is safe to ask the model

    Parameters:
        question (str): The question to check

    Returns a list of errors if the question is not safe, otherwise returns None
    """

    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }
    response = openai.Moderation.create(input=question)
    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None


def get_chatbot_response(new_question, previous_questions_and_answers):
#    os.system("cls" if os.name == "nt" else "clear")
    # keep track of previous questions and answers
#    previous_questions_and_answers = []
#    while True:
        # ask the user for their question
#    new_question = input(
#        Fore.GREEN + Style.BRIGHT + "What can I get you?: " + Style.RESET_ALL
#    )
    # check the question is safe
    errors = get_moderation(new_question)
    if errors:
        error_part_1 = (
            Fore.RED
            + Style.BRIGHT
            + "Sorry, you're question didn't pass the moderation check:"
        )
        errors_list = []
        for error in errors:
            errors_list.append(error)
#        print(Style.RESET_ALL)
        return error_part_1 + "\n".join(errors_list) + Style.RESET_ALL
    # build the previous questions and answers into the prompt
    # use the last MAX_CONTEXT_QUESTIONS questions
    context = ""
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        context += QUESTION_SEQUENCE + question + ANSWER_SEQUENCE + answer

    # add the new question to the end of the context
    context += QUESTION_SEQUENCE + new_question + ANSWER_SEQUENCE

    # get the response from the model using the instructions and the context
    response = get_response(INSTRUCTIONS + context)

    # add the new question and answer to the list of previous questions and answers
    previous_questions_and_answers.append((new_question, response))

    # print the response
    return response



def get_chatbot(new_question):
    previous_questions_and_answers = []
#    while True:
    return get_chatbot_response(new_question, previous_questions_and_answers)
