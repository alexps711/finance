from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

@app.route("/")
@login_required
def index():
    return apology("TODO")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "POST":
        if lookup(request.form.get("symbol")) == None:
            return apology("Symbol does not exist")

        cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])
        real_cash = cash[0]["cash"]
        quote = lookup(request.form.get("symbol"))
        total_price = int(quote["price"]) * int(request.form.get("shares"))

        if real_cash < total_price:
            return apology("You do not have enough cash!!")
        else:
            #log table does not work
            db.execute("INSERT INTO log (symbol, price) VALUES (:symbol , :price)", symbol = quote["symbol"], price = quote["price"])
            return redirect(url_for("index"))

    else:
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    return apology("TODO")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide symbol")
        elif lookup(request.form.get("symbol")) != None:
            quote = lookup(request.form.get("symbol"))
            return render_template("quoted.html", name= quote["name"], price= quote["price"])
        else:
            return apology("symbol does not exist")
    else:
        return render_template("quote.html")
@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username")
        elif not request.form.get("password"):
            return apology("must provide password")
        #hash password
        password_hash = pwd_context.hash(request.form.get("password"))
        #compare passwords provided by the user match
        if not pwd_context.verify(request.form.get("cpassword"), password_hash):
            return apology("password does not match")
        #insert name and username into database
        result = db.execute("INSERT INTO users (username, hash) VALUES (:username, :password_hash)", username = request.form.get("username"), password_hash = password_hash)
        if not result:
            return apology("Username already exists")
        #query database for user id
        rows= db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        #store user's id
        session["user_id"] = rows[0]["id"]
        return redirect(url_for("index"))
    else:
        return render_template("register.html")
@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    return apology("TODO")

@app.route("/password", methods=["GET", "POST"])
def password():

    if request.method == "POST":
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if len(rows) != 1:
            return apology("This username does not exist")
        else:
            return redirect(url_for("password2"))
    else:
        return render_template("password.html")

@app.route("/password2", methods=["GET", "POST"])
def password2():

    if request.method == "POST":

        old_password = db.execute("SELECT hash FROM users WHERE username = :username", username = request.form.get("username"))
        real_old_password = old_password[0]
        if pwd_context.verify(request.form.get("password"), old_password):
            return apology("THIS WAS YOUR PASSWORD!!!!!")
        elif request.form.get("password") == request.form.get("passwordver"):
            new_password = pwd_context.hash(request.form.get("password"))
            update = db.execute("UPDATE users SET hash = :hash WHERE username = :username", hash=new_password, username = request.form.get("username"))
    else:
        return render_template("password2.html")