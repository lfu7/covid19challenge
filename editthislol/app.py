import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

#API_KEY
#pk_53b5c4f1c3664a5190f6ed7dc603f94e

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
#app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
##
# Make sure API key is set
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():

@app.route("/patient", methods=["GET", "POST"])
@login_required
def patient():
    #TODO: if submitted form already, get waittime
    if request.method == "GET":
        #form
        return render_template("patient.html")
    else:
        #grab stuff from form
        return render_template("waittime.html")


    '''
    if request.method == "GET":
        #interface patient.html (request new visit/existing visit, past visit)
        return render_template(patient.html)
    else:
        #grab stuff from form
        return redirect("/patientform")

    '''



@app.route("/hospital", methods=["GET", "POST"])
@login_required
def hospital():
    if request.method == "GET":
        return render_template("hospital.html")
        #hospital.html has managing resources, select decision policy, queue
        #(maybe in nav bar, have hospital_layout.html)
@app.route("/resources", methods=["GET", "POST"])
@login_required
def hospital_resources():
    #input/initialize what resources you have
    #display resources in resources.html (beds whatever)

@app.route("/queue", methods=["GET", "POST"])
@login_required
def hospital_queue():
    #form tells you based on policy, what patients you should consider admitting
    #what resources they Required

    #if you do admit, you can update hospital_resources what resources you allocated (talk to db)

@app.route("/policy", methods=["GET", "POST"])
@login_required
def hospital_policy():
    if request.method == "GET":
        #render form
    #form where you can toggle policy
    #have some arbitrary number scoring system
    #what you prioritize or whatnot (age, risk, symptoms, covid/non-covid)
    #also have premade algorithm
    else:
        #submit/update policy info for hospital


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        #grab boolean from login form
        patient = request.form.get("type")
        #if your patients
        if (patient):
            return redirect("/patient")
        else:
            return redirect("/hospital")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    #TODO: modify to register as patient or hospital

    # Forget any user_id (not sure if necessary)
    # session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            return apology("must provide password", 400)

        # Ensure password was confirmed
        confirmation = request.form.get("confirmation")
        if not confirmation or (confirmation != password):
            return apology("must provide a valid confirmation", 400)

        db.execute("INSERT INTO users (username, hash) VALUES(:un, :h)",
            un=request.form.get("username"), h=generate_password_hash(password))

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
