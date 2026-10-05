import os
import uuid  # for public id
from datetime import datetime, timedelta
from functools import wraps

import jwt
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash

from chatbot import get_chatbot
from db import Diary, User, Weather

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['MONGODB_SETTINGS'] = {
    'db': "health_app",
    'host': "mongodb://127.0.0.1:27017/"
}
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-only-secret")


@app.route("/")
def index_get():
    return render_template("index.html")


@app.route("/api/talk", methods=['POST'])
def talk():
    user_input = request.json["message"]
    response = get_chatbot(user_input)
    return jsonify({"answer": response})


# Route for the chatbot home page
@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', error=None)


# Route for the main home page
@app.route('/mainhome', methods=['GET', 'POST'])
def mainhome():
    return render_template('mainhome.html', error=None)


@app.route("/track_emotion", methods=['POST'])
def get_emotion_from_text():
    import text2emotion as te
    text = request.json["text"]
    emotions = te.get_emotion(text)
    return jsonify({"answer": emotions})


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token') or request.cookies.get('token')
        if not token:
            return jsonify({'message': 'Token is missing !!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.objects(public_id=data['public_id']).first()
        except Exception:
            return jsonify({'message': 'Token is invalid !!'}), 401
        # pass the current logged in user's context to the route
        return f(current_user, *args, **kwargs)

    return decorated


# route for logging a user in
@app.route("/login", methods=['POST'])
def login():
    username = request.form.get('username2')
    password = request.form.get('password2')

    if not username or not password:
        return make_response(
            'Could not verify', 401,
            {'WWW-Authenticate': 'Basic realm ="Login required !!"'}
        )

    user = User.objects(name=username).first()
    if not user:
        return make_response(
            'Could not verify', 401,
            {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'}
        )

    if check_password_hash(user.password, password):
        token = jwt.encode({
            'public_id': user.public_id,
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        response = make_response(redirect(url_for('home')))
        response.set_cookie('token', token, httponly=True)
        return response

    return make_response(
        'Could not verify', 403,
        {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'}
    )


# signup route
@app.route("/signup", methods=['POST'])
def signup():
    name = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    # check for an existing user
    user = User.objects(email=email).first()
    if not user:
        User(
            public_id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=generate_password_hash(password)
        ).save()
        return redirect(url_for('home'))

    return make_response('User already exists. Please Log in.', 202)


@app.route("/user_profile", methods=['POST'])
def fill_user_profile():
    name = request.form["name"]
    User.objects(name=name).update(
        age=int(request.form["age"]),
        city=request.form["city"],
        state=request.form["state"],
        country=request.form["country"]
    )
    return jsonify({
        "state": "SUCCESS",
        "status": "Profile completed"
    })


@app.route('/diary', methods=['GET', 'POST'])
def diary():
    return render_template('diary.html')


@app.route('/findothers', methods=['GET', 'POST'])
def findothers():
    return render_template('findothers.html', error=None)


@app.route('/diary/save', methods=['POST'])
def save_note():
    Diary(
        name=request.form["name"],
        date=datetime.now(),
        mood=request.form["mood"],
        sleep=request.form["sleep"],
        note=request.form["note"]
    ).save()
    return {
        "state": "Success",
        "status": "Note saved"
    }


@app.route('/diary/num_logged_days', methods=['GET'])
def get_num_logged_days():
    name = request.args["name"]
    num_records = Diary.objects(name=name).count()
    return {
        "state": "Success",
        "status": num_records
    }


def trigger_weather_api(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return None
    url = f"http://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={city}"
    return requests.get(url).json()


@app.route('/get_weather_report', methods=['GET'])
def get_weather_report():
    name = request.args["name"]
    city = User.objects.get(name=name).city

    response = trigger_weather_api(city)
    if response is None:
        # no API key configured: fall back to canned demo data
        Weather(
            city=city,
            date=datetime.now(),
            temperature="23",
            pressure="30",
            humidity="73",
            weather="mostly cloudy",
        ).save()
    elif response.get("cod") == "404":
        return {
            "state": "FAILURE",
            "status_code": "404",
            "message": "Failed to get weather report of your city"
        }
    else:
        main_details = response["main"]
        Weather(
            city=city,
            date=datetime.now(),
            temperature=str(main_details["temp"]),
            pressure=str(main_details["pressure"]),
            humidity=str(main_details["humidity"]),
            weather=response["weather"][0]["description"],
        ).save()

    return jsonify({
        "state": "SUCCESS",
        "status": "Weather report saved"
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
