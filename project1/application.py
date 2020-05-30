import os, requests

from flask import Flask, jsonify, session, render_template, redirect, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import error, login_required

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


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Clear session
    session.clear()

    # If route reached via "POST" method
    if request.method == "POST":

        # Select user's data from the database
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": request.form.get("username")}).fetchone()

        # Ensure username exists and password is correct
        if rows == None or not check_password_hash(rows["password"], request.form.get("password")):
            wronginput = True
            return render_template("login.html", wronginput=wronginput)

        # Remember which user has logged in
        session["user_id"] = rows["id"]

        # Redirect user to search page
        return redirect(url_for('search'))

    # If user reached route via "GET" method
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    # If route reached via "POST" method
    if request.method == "GET":
        return render_template("register.html")

    # If user reached route via "GET" method
    else:
        username = request.form.get("username")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchall()

        # Ensure username does not already exist in the database
        if len(rows) == 1:
            userexists = True
            return render_template('register.html', userexists=userexists)

        # Ensure username is no longer than 32 characters
        if len(username) > 32:
            longuser = True
            return render_template('register.html', longuser=longuser)

        # Ensure username contains only alphanumeric characters
        for char in username:
            if not char.isalnum() == True:
                wronguser = True
                return render_template('register.html', wronguser=wronguser)

        email = request.form.get("e-mail")

        # Query database for e-mail
        rows = db.execute("SELECT * FROM users WHERE email = :email", {"email": email}).fetchall()

        # Ensure e-mail does not already exist in the database
        if len(rows) == 1:
            emailexists = True
            return render_template('register.html', emailexists=emailexists)

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure password and confirmation match
        if not password == confirmation:
            pasnotcon = True
            return render_template('register.html', pasnotcon=pasnotcon)

        # Ensure password is 8 or more characters
        if len(password) < 8:
            shortpass = True
            return render_template('register.html', shortpass=shortpass)

        # Insert new user into database
        db.execute("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)",
                   {"username": username, "password": generate_password_hash(password, method='pbkdf2:sha256', salt_length=8), "email": email})
        db.commit()

        # Redirect user to the login page
        return redirect(url_for('login'))

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():

    # If route reached via "POST" method
    if request.method == "GET":
        return render_template("search.html")

    # If user reached route via "GET" method
    else:
        isbn_input = request.form.get("isbn")
        title_input = request.form.get("title")
        author_input = request.form.get("author")

        # If user searched by ISBN
        if isbn_input:

            # Ensure ISBN input has at least one alphanumeric character
            haschar = False
            wronginput = False
            for char in isbn_input:
                if char.isalnum() == True:
                    haschar = True
            if haschar == False:
                wronginput = True
                return render_template("search.html", wronginput=wronginput)

            # Query database for isbn, title, author and year
            rows = rows = db.execute("SELECT books.isbn as isbn, title, year, name FROM books INNER JOIN authors ON books.isbn=authors.isbn INNER JOIN people ON authors.person_id=people.id WHERE books.isbn ILIKE :isbn ORDER BY isbn", {'isbn': f"%{isbn_input}%"}).fetchall()

        # If user searched by title
        if title_input:

            # Ensure title input has at least one alphanumeric character
            haschar = False
            wronginput = False
            for char in title_input:
                if char.isalnum() == True:
                    haschar = True
            if haschar == False:
                wronginput = True
                return render_template("search.html", wronginput=wronginput)

            # Query database for isbn, title, author and year
            rows = db.execute("SELECT books.isbn as isbn, title, year, name FROM books INNER JOIN authors ON books.isbn=authors.isbn INNER JOIN people ON authors.person_id=people.id WHERE title ILIKE :title ORDER BY title", {'title': f"%{title_input}%"}).fetchall()

        # If user searched by author
        if author_input:

            # Ensure author input has at least one alphanumeric character
            haschar = False
            wronginput = False
            for char in author_input:
                if char.isalnum() == True:
                    haschar = True
            if haschar == False:
                wronginput = True
                return render_template("search.html", wronginput=wronginput)

            # Query database for author
            rows = db.execute("SELECT books.isbn as isbn, title, year, name FROM books INNER JOIN authors ON books.isbn=authors.isbn INNER JOIN people ON authors.person_id=people.id WHERE name ILIKE :name ORDER BY name, title", {'name': f"%{author_input}%"}).fetchall()

        return render_template("results.html", rows=rows)

@app.route("/books/<string:isbn>", methods=["GET", "POST"])
@login_required
def books(isbn):

    # Query database for isbn, title and year
    rows = db.execute("SELECT books.isbn as isbn, title, year, name FROM books INNER JOIN authors ON books.isbn=authors.isbn INNER JOIN people ON authors.person_id=people.id WHERE books.isbn ILIKE :isbn ORDER BY isbn", {"isbn": str(isbn)}).fetchone()

    # If provided isbn not in db, raise 404 error
    if rows is None:
        return error("Isbn not found.", 404)
    else:

        # Query database for reviews
        review_displayer = db.execute("SELECT review, rating, username, header, timestamp FROM reviews JOIN users ON users.id = reviews.user_id WHERE isbn = :isbn ORDER BY timestamp DESC",
                                      {"isbn": str(isbn)}).fetchall()

        # Query database for reviews written by logged-in user
        review_checker = db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND user_id = :user_id",
                                    {"isbn": str(isbn), "user_id": session["user_id"]}).fetchone()

        # Declare variable with API key from Goodreads
        apikey = "xPAks8w53q3aGgNbKxygpQ"
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": apikey, "isbns": str(isbn)})
        if res.status_code != 200:
            raise Exception("ERROR: API request unsuccessful.")
        data = res.json()
        goodcount = data["books"]["work_ratings_count"]
        goodrating_list = data["books"]["average_rating"]

        # Query database for local average rating and rating count
        current_rating = db.execute("SELECT AVG(rating) as average, COUNT (rating) as count FROM reviews WHERE isbn = :isbn",
                                    {"isbn": str(isbn)}).fetchone()

        # If user reached route via "POST" (after user have left a review)
        if request.method == "POST":
            review = request.form.get("review")
            rating = request.form.get("rating")
            header = request.form.get("header")

            # Ensure review is no longer than 500 characters and its title is no longer than 32 characters
            longreview = False
            if len(review) > 500 or len(header) > 32:
                longreview = True
                return render_template("books.html", longreview=longreview, review_displayer=review_displayer, review_checker=review_checker, current_rating=current_rating, goodcount=goodcount, goodrating=goodrating, rows=rows)

            # Ensure title of review has at least one alphanumeric character
            haschars = False
            wrongtitle = False
            for char in header:
                if char.isalnum() == True:
                    haschars = True
            if haschars == False:
                wrongtitle = True
                return render_template("books.html", wrongtitle=wrongtitle, longreview=longreview, review_displayer=review_displayer, review_checker=review_checker, current_rating=current_rating, goodcount=goodcount, goodrating=goodrating, rows=rows)

            # If review does not contain any alphanumeric character, set its value to 'No review'
            haschars1 = False
            for char in review:
                if char.isalnum() == True:
                    haschars1 = True
            if haschars1 == False:
                review = 'No review'


            # Check if user has already added a review to avoid adding same one by refreshing the page
            if not review_checker:
                # Insert into database, adding user's id, review and rating
                db.execute("INSERT INTO reviews (user_id, isbn, review, rating, header) VALUES (:user_id, :isbn, :review, :rating, :header)",
                           {"user_id": session["user_id"], "isbn": str(isbn), "review": review, "rating": rating, "header": header})
                db.commit()

                # Update review_displayer, review_checker and current_rating
                review_displayer = db.execute("SELECT review, rating, username, header, timestamp FROM reviews JOIN users ON users.id = reviews.user_id WHERE isbn = :isbn ORDER BY timestamp DESC",
                                              {"isbn": str(isbn)}).fetchall()
                review_checker = db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND user_id = :user_id",
                                        {"isbn": str(isbn), "user_id": session["user_id"]}).fetchone()
                current_rating = db.execute("SELECT AVG(rating) as average, COUNT (rating) as count FROM reviews WHERE isbn = :isbn",
                                            {"isbn": str(isbn)}).fetchone()

                return render_template("books.html", review_displayer=review_displayer, review_checker=review_checker, current_rating=current_rating, goodcount=goodcount, goodrating=goodrating, rows=rows)

        return render_template("books.html", review_displayer=review_displayer, review_checker=review_checker, current_rating=current_rating, goodcount=goodcount, goodrating=goodrating, rows=rows)


@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):

    # Query database for isbn
    books = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": str(isbn)}).fetchone()

    # Query database for the average rating and rating count
    reviews = db.execute("SELECT AVG(rating) as average, COUNT (rating) as count FROM reviews WHERE isbn = :isbn", {"isbn": str(isbn)}).fetchone()

    # If isbn doesn't exist in database, return 404 error
    if books is None:
          return error("API not found", 404)

    # Query database for authors name
    authors = db.execute("SELECT name FROM people JOIN authors ON  authors.person_id = people.id WHERE isbn=:isbn", {'isbn': books.isbn}).fetchone()

    # Jsonify pertinent data
    return jsonify({
              "isbn": books.isbn,
              "title": books.title,
              "author": authors.name,
              "year": books.year,
              "average_score": float(reviews.average),
              "review_count": reviews.count
          })


# Errorhandler
def handler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(handler)
