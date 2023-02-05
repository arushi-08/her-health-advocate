import io
import requests
from flask import Flask, render_template, jsonify, request, make_response, redirect, url_for, Response
from flask_cors import CORS
import uuid # for public id
from  werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
# imports for PyJWT authentication
import jwt
from datetime import datetime, timedelta
from functools import wraps
import text2emotion as te

from chatbot import get_chatbot
from db import User, Diary, Weather

app = Flask(__name__)
CORS(app)
app.config['MONGODB_SETTINGS'] = {
    'db': "health_app",
    'host': "mongodb://127.0.0.1:27017/"
}
app.config['SECRET_KEY'] = "123"


@app.route("/")
def index_get():
    return render_template("index.html")
    
    
@app.route("/api/talk", methods=['POST'])
def index():
    user_input = request.json["message"]
    response = get_chatbot(user_input)
    print(response)
    return jsonify({"answer": response})

# Route for handling the login page logic
@app.route('/home', methods=['GET', 'POST'])
def home():
    error=None

    return render_template('home.html', error=error)

# Route for handling the main home page logic
@app.route('/mainhome', methods=['GET', 'POST'])
def mainhome():
    error=None

    return render_template('mainhome.html', error=error)

  
@app.route("/track_emotion", methods =['POST'])
def get_emotion_from_text():
    text = request.json["text"]
    emotions = te.get_emotion(text)
    return jsonify({"answer": emotions})


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query\
                .filter_by(public_id = data['public_id'])\
                .first()
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        # returns the current logged in users contex to the routes
        return  f(current_user, *args, **kwargs)
  
    return decorated
  
# route for logging user in
@app.route("/login", methods =['POST'])
def login():
    # creates dictionary of form data
    auth = request.form
  
    if not auth or not auth.get('username2') or not auth.get('password2'):
        # returns 401 if any email or / and password is missing
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
        )
  
    user = User.objects(email = auth.get('email')).first()
  
    if not user:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
        )
    print(user.password)
    print(auth.get('password'))
    if check_password_hash(user.password, auth.get('password')):
        # generates the JWT Token
        token = jwt.encode({
            'public_id': user.public_id,
            'exp' : datetime.utcnow() + timedelta(minutes = 30)
        }, app.config['SECRET_KEY'])
  
        return make_response(jsonify({'token' : token.decode('UTF-8')}), 201)
    # returns 403 if password is wrong
    return make_response(
        'Could not verify',
        403,
        {'WWW-Authenticate' : 'Basic realm ="Wrong Password !!"'}
    )
  
# signup route
@app.route("/signup", methods =['POST'])
def signup():
    # creates a dictionary of the form data
    # print(request)
    # gets name, email and password
    name, email = request.form["username"], request.form["email"]
    password = request.form["password"]
    print('name',name)
    print('email',email)
    print('password',password)
  
    # checking for existing user
    user = User.objects(email = email).first()
    
    if not user:
        # database ORM object
        User(
            public_id = str(uuid.uuid4()),
            name = name,
            email = email,
            password = generate_password_hash(password)
        ).save()
  
        return redirect(url_for('home'))
    else:
        # returns 202 if user already exists
        return make_response('User already exists. Please Log in.', 202)


@app.route("/user_profile", methods =['POST'])
def fill_user_profile():
    name = request.form["name"]
    age = int(request.form["age"])
    city = request.form["city"]
    state = request.form["state"]
    country = request.form["country"]
    User.objects(name=name).update(
        age=age,
        city=city,
        state=state,
        country=country
    )
    return jsonify({
        "state": "SUCCESS",
        "status": "Profile completed"
        })


# Route for handling the main home page logic
@app.route('/diary', methods=['GET', 'POST'])
def diary():
    
    return render_template('diary.html')

# Route for handling the main home page logic
@app.route('/findothers', methods=['GET', 'POST'])
def findothers():
    error=None
    return render_template('findothers.html', error=error)

@app.route('/diary/save', methods=['POST'])
def save_note():
    name = request.form["name"]
    mood = request.form["mood"]
    sleep_hours = request.form["sleep"]
    note = request.form["note"]
    Diary(
        name=name,
        date=datetime.now(),
        mood=mood,
        sleep=sleep_hours,
        note=note
    ).save()

    return {
        "state": "Success",
        "status": "Note saved"
        }


@app.route('/diary/num_logged_days', methods=['GET'])
def get_num_logged_days():
    name = request.form["name"]
    num_records = Diary.objects(name=name).count()
    return {
        "state": "Success",
        "status": num_records
        }


def trigger_weather_api(city):
    # Enter your API key here
    api_key = "aa627c9d7a56918d5e7ef50d37e44f28"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city
    requests.get(complete_url).json()
    

@app.route('/get_weather_report', methods=['GET'])
def get_weather_report():
    name = request.form["name"]
    city = User.objects.get(name=name).city
    print(city)
    # response = trigger_weather_api(city)
    response = {"cod": "200"}
    print(response)
    if response["cod"] == "404":
        return {
            "state": "FAILURE",
            "status_code": "404",
            "message": "Failed to get weather report of your city"
        }
    
    Weather(
        city=city,
        date=datetime.now(),
        temperature="23",
        pressure="30",
        humidity="73",
        weather="mostly cloudy",
    ).save()

    # main_details = response["main"]
    # Weather(
    #     city=city,
    #     date=datetime.now(),
    #     temperature=main_details["temp"],
    #     pressure=main_details["pressure"],
    #     humidity=main_details["humidity"],
    #     weather=main_details["weather"],
    # ).save()
    return jsonify({
        "state": "SUCCESS",
        "status": "Weather report saved"
        })


# def report_sleep_chart():
#     # name = request.form["name"]
#     name = "Arushi"
#     date = datetime.now() - timedelta(7)
#     records = Diary.objects(name=name, date__gte=date)
#     sleep_hours = [r.sleep for r in records]
#     date_list = [datetime.now() - timedelta(days=x) for x in range(7)]
#     plt.plot(date_list, sleep_hours)


# @app.route('/plot.png')
# def plot_png():
#     fig = report_sleep_chart()
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')


if __name__ == "__main__":
#    main()
    app.run(host="127.0.0.1", port=8000, debug=True)
