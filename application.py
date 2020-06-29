import os

import flask
from flask import Flask, session, render_template, request, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
import requests

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/",  methods=["GET","POST"])
def index():
    return redirect("/login")


@app.route("/login",  methods=["GET","POST"])
def login():
    session.clear()
    if flask.request.method == 'GET':
        return render_template("index.html")
    else:
        username = request.form.get("username")
        # check if username exists
        user_exist = db.execute("SELECT * FROM users WHERE username = :username",
                                {"username": username}).fetchone()

        if user_exist == None:
            flash("Invalid username and/or password")
            return render_template("index.html")

        # get password from form
        password = request.form.get("password")
        # check for correct password

        if not check_password_hash(user_exist[3], password):
            flash("Invalid username and/or password")
            return render_template("index.html")

        session["name"] = user_exist[0].capitalize()
        session["username"] = user_exist[2]
        session["logged_in"] = True
        return render_template("search.html")


@app.route("/register",  methods=["GET","POST"])
def register():
    if session.get("logged_in"):
        session.clear()
    if flask.request.method == 'POST':
        # getting form elements
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        #verify existing username
        user_exist = db.execute("SELECT * FROM users WHERE username = :username",
                               {"username": username}).fetchone()

        # Check if username currenlty in database
        if user_exist:
            return render_template("error.html", message="Username is taken.")

        #verify both passwords
        if password != password2:
            return render_template("error.html", message = "Passwords didn't match")

        #hashhing user password
        pw_hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        #insert into database
        db.execute("INSERT INTO users (fname, lname, username, pw_hash) VALUES (:fname, :lname, :username, :password)",
                   {"fname": fname, "lname": lname,"username": username,
                    "password": pw_hash})
        db.commit()
        return redirect("/login")

    # any other requests except post
    return render_template("register.html")

@app.route("/search",  methods=["GET","POST"])
def search():
    if request.method == "GET":
        return redirect("/login")
    else:
        if not session.get("logged_in"):
            flash("You are not logged in")
            return redirect("/login", "303")
        search_text = request.form.get("search-text")
        criteria = request.form.get("criteria")
        if criteria == "0":
            search_text = "%"+search_text+"%"
            books = db.execute("SELECT * FROM books WHERE isbn LIKE :search_text \
                               OR author LIKE :search_text \
                               OR pub_year LIKE :search_text \
                                OR title = :search_text",
                                    {"search_text": search_text}).fetchall()
        elif criteria == "1":
            search_text = "%" + search_text + "%"
            books = db.execute("SELECT * FROM books WHERE author LIKE :search_text",
                               {"search_text": search_text}).fetchall()
        elif criteria == "2":
            search_text = "%" + search_text + "%"
            books = db.execute("SELECT * FROM books WHERE pub_year LIKE :search_text",
                               {"search_text": search_text}).fetchall()
        elif criteria == "3":
            search_text = "%" + search_text + "%"
            books = db.execute("SELECT * FROM books WHERE title LIKE :search_text",
                               {"search_text": search_text}).fetchall()
        elif criteria == "4":
            search_text = "%" + search_text + "%"
            books = db.execute("SELECT * FROM books WHERE isbn LIKE :search_text",
                               {"search_text": search_text}).fetchall()

        if books:
            return render_template("search.html", books = books)

        return render_template("search.html", books= {})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/book/<isbn>",methods=["POST", "GET"])
def book(isbn):
    if not session.get("logged_in"):
        flash("You are not logged in")
        return redirect("/login", "303")

    if flask.request.method=="GET":
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                           {"isbn": isbn}).fetchone()

        goodread_key = os.getenv("GOODREADS_KEY")

        # get goodread JSON
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                             params={"key": goodread_key, "isbns": book[0]})

        res = res.json()

        # get the correct JSON list
        goodread = res['books'][0]

        #reviews
        reviews = db.execute("SELECT users.username, comment, rating \
                                    FROM users \
                                    INNER JOIN reviews \
                                    ON users.username = reviews.username\
                                    WHERE reviews.isbn = :isbn", {"isbn": isbn}).fetchall()
        #print(reviews[0])
        return render_template("book.html", book=book, goodread=goodread, reviews=reviews)

    else:
        rating = request.form.get("rating")
        rating = int(rating)
        comment = request.form.get("comment")
        username = session["username"]

        query = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn=:isbn", {"username":username, "isbn": isbn})
        if query.rowcount>0:
            return render_template("error.html", message="You already submitted a review for this book")
           # flash('You already submitted a review for this book', 'warning')
            #return redirect("/book/" + isbn)


        db.execute("INSERT INTO reviews (username, isbn, comment, rating) VALUES \
                            (:username, :isbn, :comment, :rating)",
                   {"username": username,
                    "isbn": isbn,
                    "comment": comment,
                    "rating": rating})
        db.commit()

        return redirect("/book/" + isbn)

@app.route("/api/<isbn>", methods=['GET'])
def api_call(isbn):

    # COUNT returns rowcount
    # SUM returns sum selected cells' values
    # INNER JOIN associates books with reviews tablesl
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                      {"isbn": isbn}).fetchone()
    if not book:
        return jsonify({"Error": "Invalid book ISBN"}), 404

    row = db.execute("SELECT \
                    COUNT(*) as review_count, \
                    AVG(reviews.rating) as average_rating \
                    FROM reviews \
                    WHERE isbn=:isbn ",  {"isbn": isbn}).fetchone()
    element = dict(row.items())
    if element['average_rating'] is None:
        element['average_rating'] = "0"
    else:
        element['average_rating'] = str(round(element['average_rating'], 2))
    result = {
        "title": book["title"],
        "author":  book["author"],
        "year":  book["pub_year"],
        "isbn":  book["isbn"],
        "review_count": element['review_count'],
        "average_score": element['average_rating']
    }
    return jsonify(result)

