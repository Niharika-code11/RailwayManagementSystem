from rail_api import get_trains, get_seat_availability, get_live_status
from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime
from flask_mail import Mail, Message
from flask import make_response  # At the top with other imports
import io
app = Flask(__name__, template_folder="Templates")
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'chsiddu2002@gmail.com'
app.config['MAIL_PASSWORD'] = '****'  # Google App Password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

USERS_FILE = 'users.json'

@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/t&c")
def tandc():
    return render_template("t&c.html")

@app.route("/privacypolicy")
def privacy():
    return render_template("privacypolicy.html")

@app.route("/register1")
def register1():
    return render_template("registration1.html")

@app.route("/register2", methods=["POST"])
def register2():
    username = request.form["username"]
    password = request.form["password"]
    securityquestion = request.form["securityquestion"]
    securityanswer = request.form["securityanswer"]

    session['registername'] = username

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    else:
        users = []

    for user in users:
        if user['username'] == username:
            return render_template('registration1.html', validuserid="(User Id already present)")

    users.append({
        'username': username,
        'password': password,
        'securityquestion': securityquestion,
        'securityanswer': securityanswer
    })

    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

    return render_template('registration2.html')

@app.route("/register3", methods=["POST"])
def register3():
    username = session.get('registername', None)
    user_info = {
        'fname': request.form["fname"],
        'mname': request.form["mname"],
        'lname': request.form["lname"],
        'occupation': request.form["occupation"],
        'dob': request.form["DOB"],
        'maritalstatus': request.form["martialstatus"],
        'country': request.form["country"],
        'sex': request.form["sex"],
        'email': request.form["email"],
        'mobileno': request.form["mobileno"]
    }

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    else:
        users = []

    for user in users:
        if user['username'] == username:
            user.update(user_info)
            break

    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

    return render_template('registration3.html')

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login1", methods=["POST"])
def login1():
    username = request.form.get("username")
    password = request.form.get("password")
    session['ID'] = username

    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    else:
        users = []

    user_match = next((u for u in users if u['username'] == username), None)
    if user_match:
        if user_match['password'] == password:
            return redirect(url_for('searchpage'))
        else:
            return render_template('login.html', validpassword="(Password incorrect)")
    else:
        return render_template('login.html', validuserid="(Wrong credentials)")

@app.route("/searchpage")
def searchpage():
    return render_template('search.html')
@app.route("/search", methods=['POST'])
def search():
    src = request.form['src']
    dest = request.form['dest']
    date = datetime.strptime(request.form['date'], '%Y-%m-%d')
    try:
        trains = get_trains(src, dest, date)
        if not trains:
            return render_template('search.html', message="No trains found for this route.", trains=[])
        return render_template('search.html', trains=trains)
    except Exception as e:
        return render_template('search.html', message=f"Error: {str(e)}", trains=[])


@app.route("/ticket/download", methods=["POST"])
def download_ticket():
    from flask import jsonify
    ticket_data = json.loads(request.form["ticket_data"])

    ticket_text = f"""
Train Ticket Confirmation

Passenger Name: {ticket_data['passenger_name']}
Age: {ticket_data['age']}
Gender: {ticket_data['gender']}
Train Number: {ticket_data['train_number']}
Class: {ticket_data['class_type']}
Fare: ₹{ticket_data['fare']}
Seats Booked: {ticket_data['seats']}
Booking Date: {ticket_data['date']}
"""

    response = make_response(ticket_text)
    response.headers["Content-Disposition"] = "attachment; filename=ticket.txt"
    response.headers["Content-Type"] = "text/plain"
    return response

@app.route("/npass/<train_number>/<fare>/<cls>/<seats>", methods=["GET", "POST"])
def passenger_details(train_number, fare, cls, seats):
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        email = request.form.get("email")
        phone = request.form.get("phone")
        category = request.form.get("category")
        date = request.form.get("date")
        src = request.form.get("src")
        dest = request.form.get("dest")
        

        ticket_id = f"TKT{train_number}{phone[-4:]}"
        
        return render_template("ticket.html",
            name=name,
            age=age,
            gender=gender,
            email=email,
            phone=phone,
            cls=cls,
            fare=fare,
            train_number=train_number,
            src=src,
            dest=dest,
            date=date,
            category=category,
            ticket_id=ticket_id
            
        )

    return render_template("passenger.html", train_number=train_number, fare=fare, cls=cls, seats=seats)


if __name__ == "__main__":
    app.run(debug=True)
