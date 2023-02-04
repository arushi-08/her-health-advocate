from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from chatbot import get_chatbot

app = Flask(__name__)
CORS(app)


@app.route("/")
def index_get():
    return render_template("base.html")
    
    
@app.route("/api/talk", methods=['POST'])
def index():
    user_input = request.json["message"]
    response = get_chatbot(user_input)
    print(response)
    return jsonify({"answer": response})

# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)
    
    
if __name__ == "__main__":
#    main()
    app.run(host="127.0.0.1", port=8000, debug=True)
