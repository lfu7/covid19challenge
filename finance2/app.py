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
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    userid=session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :id", id=userid)
    # Ensure id exists
    if len(user) != 1:
        return apology("invalid userid", 400)

    stonks = db.execute("SELECT * FROM stocks WHERE userid = :id", id=userid)
    #update value of the stonks and sum up value of stocks
    sum = 0
    for stonk in stonks:
        symbol = stonk['symbol']
        price = lookup(symbol)['price']
        db.execute("UPDATE stocks SET price = :price WHERE userid = :usid AND symbol = :symbol",
            usid=userid, symbol=symbol, price = price)
        sum += price * stonk['shares']
    stonks = db.execute("SELECT * FROM stocks WHERE userid = :id", id=userid)
    return render_template("index.html", user=user[0], stonks=stonks, stonk_sum=sum)



@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    if (len(username) == 0):
        return jsonify(False)
    matches = db.execute("SELECT * FROM users WHERE username = :uname", uname=username)
    if (len(matches) == 0):
        return jsonify(True)
    else:
        return jsonify(False)

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
