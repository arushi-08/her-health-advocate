# Command Line Chat Bot

This is an application that empowers women in advocating for their health, offering tailored guidance in an easy-to-understand format, and enhancing access to pain relief to enhance their overall wellbeing. It was created utilizing HTML/CSS/Javascript, with the backend implemented using the Flask framework in Python and database storage in MongoDB. User authentication was established with JWT, and an intelligent taskbot feature was developed using the OpenAI API.

# Setup

Make sure you have python3 installed:

```
python3 --version
```

Create a virtual environment and install the dependencies:

### Linux/Mac:

```
python3 -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
```

### Windows:

```
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

# Configuration

Copy `env.sample` to `.env` and add your OpenAI API key to the file.

```
OPENAI_API_KEY=<<YOUR_API_KEY>>
```

Edit `main.py` and replace `<<PUT THE PROMPT HERE>>` with your prompt:

e.g. Create a simple AI cocktail assistant

```
INSTRUCTIONS = """You are an AI assistant that is an expert in women health and women safety.
You know about health, lifestyle, hygiene and safety.
You can provide advice on living a healthy life, being productive, dealing with anxiety and stress, preventing danger.
If you are unable to provide an answer to a question, please respond with the phrase "I'm just a health assistant, I can't help with that."
Please aim to be as helpful, creative, and friendly as possible in all of your responses.
Do not use any external URLs in your answers. Do not refer to any blogs in your answers.
Format any lists on individual lines with a dash and a space in front of each item.
"""
```

# Running

To run just do the following:

### Linux/Mac:

```
. ./venv/bin/activate
python main.py
```

### Windows:

```
venv\Scripts\activate.bat
python main.py
```
