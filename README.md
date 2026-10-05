# Her Health Advocate

> Built at **SheInnovates 2023** — the original hackathon prototype, cleaned up so it still runs today. The pitch deck is in [`SheInnovates 2023 - Her Health Advocate.pptx`](SheInnovates%202023%20-%20Her%20Health%20Advocate.pptx).

Her Health Advocate empowers women to advocate for their own health. It offers tailored guidance in an easy-to-understand format and makes wellbeing support more accessible.

## Features

- **Maya, an AI health chat assistant** — answers questions about health, lifestyle, hygiene, and safety (OpenAI API, with moderation on every message)
- **Daily diary** — log mood, sleep hours, and notes, with emotion tracking from diary text (`text2emotion`)
- **User accounts** — signup/login with hashed passwords and JWT sessions
- **Weather-aware wellbeing** — pulls local weather for the user's city (OpenWeatherMap)
- **Find Others** — connect with other women in your community

## Tech stack

HTML/CSS/JavaScript frontend, Flask (Python) backend, MongoDB for storage, JWT for authentication, and the OpenAI API for the chat assistant.

## Setup

Requires Python 3.10+ and a MongoDB instance on `mongodb://127.0.0.1:27017` (only needed for accounts/diary — the chatbot works without it).

```bash
python3 -m venv venv
. ./venv/bin/activate        # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Configuration

Copy `env.sample` to `.env` and fill in your keys:

```
OPENAI_API_KEY=your-openai-api-key          # required for the chatbot
SECRET_KEY=change-me-to-a-random-string     # used to sign JWTs
OPENWEATHER_API_KEY=your-openweathermap-key # optional; demo data is used if unset
```

## Running

```bash
. ./venv/bin/activate
python main.py
```

Then open http://127.0.0.1:8000 — sign up, and chat with Maya from the bubble in the bottom-right corner.
