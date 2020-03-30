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
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///hospitals.db")

# Make sure API key is set
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def welcome():
    userid=session["user_id"]
    accounttype=session["account_type"]
    #patient
    if (accounttype==0):
        user = db.execute("SELECT * FROM patients WHERE id = :id", id=userid)
        # Ensure id exists
        if len(user) != 1:
            return apology("invalid userid", 400)

        return render_template("patient.html", user=user[0])

    #hospital
    elif (accounttype==1):
        user = db.execute("SELECT * FROM hospitals WHERE id = :id", id=userid)
        # Ensure id exists
        if len(user) != 1:
            return apology("invalid userid", 400)
        #if resources haven't been initialized
        if user[0]['occupied'] == None or user[0]['bedcap'] == None:
            return render_template("incomplete.html")
        return render_template("hospital.html", user=user[0])

@app.route("/manage_resources", methods=["GET", "POST"])
@login_required
def manage_resources():
    userid=session["user_id"]
    user = db.execute("SELECT * FROM hospitals WHERE id = :id", id=userid)
    if len(user) != 1:
        return apology("invalid userid", 400)
    if request.method == "GET":
        # Ensure id exists
        if request.method == "GET":
            return render_template("resources.html", user=user[0])
    #post
    else:
        bedcap = request.form.get("bedcap")
        occupied = request.form.get("occupied")
        #update query with updated stuff
        if bedcap and occupied:
            db.execute("UPDATE hospitals SET bedcap = :bedcap, occupied= :occupied WHERE id =:id",
                bedcap=bedcap, occupied=occupied, id=user[0]['id'])
        else:
            if bedcap:
                db.execute("UPDATE hospitals SET bedcap = :bedcap WHERE id =:id",
                    bedcap=bedcap, id=user[0]['id'])
            if occupied:
                db.execute("UPDATE hospitals SET occupied = :occupied WHERE id =:id",
                    occupied=occupied, id=user[0]['id'])
    return redirect("/")

    #input/initialize what resources you have
    #display resources in resources.html (beds whatever)

@app.route("/queue", methods=["GET", "POST"])
@login_required
def hospital_queue():
    if request.method == "GET":
        return render_template("queue.html")
    #form tells you based on policy, what patients you should consider admitting
    #what resources they Required
    #age, troublebreathing, preexisting condition multiplier
    #if you do admit, you can update hospital_resources what resources you allocated (talk to db)

@app.route("/decision_policy", methods=["GET", "POST"])
@login_required
def hospital_policy():
    if request.method == "GET":
        return render_template("policy.html")
        #render form
    #form where you can toggle policy
    #have some arbitrary number scoring system
    #what you prioritize or whatnot (age, risk, symptoms, covid/non-covid)
    #also have premade algorithm
    #else:
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

        # Ensure a radio button was selected
        elif not request.form.get("account_type"):
            return apology("must select button", 403)

        # checks if patient exists
        if (request.form.get("account_type") == "Patient"):
            # Query database for username
            rows = db.execute("SELECT * FROM patients WHERE username = :username",
                              username=request.form.get("username"))

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            #account_type: 0 -> patient, 1 -> hospitals
            session["account_type"] = 0

        else:
            rows = db.execute("SELECT * FROM hospitals WHERE username = :username",
                              username=request.form.get("username"))

            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                return apology("invalid username and/or password", 403)

            session["user_id"] = rows[0]["id"]
            session["account_type"] = 1

        # Redirect user to home page
        return redirect("/")

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

        # Ensure a radio button was selected
        if not request.form.get("account_type"):
            return apology("must select button", 400)

        if (request.form.get("account_type") == "Patient"):
            db.execute("INSERT INTO patients (username, hash) VALUES(:un, :h)",
            un=request.form.get("username"), h=generate_password_hash(password))

        else: #hospital
            db.execute("INSERT INTO hospitals (username, hash) VALUES(:un, :h)",
            un=request.form.get("username"), h=generate_password_hash(password))

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


#patient form
@app.route("/request_visit", methods=["GET", "POST"])
@login_required
def form():
    print("hello");
    if request.method=="POST":
        return

    else:
        return render_template("request_visit.html")




def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
