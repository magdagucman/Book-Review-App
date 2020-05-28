# Project 1

Web Programming with Python and JavaScript

This web application allows logged in users to search for books (by title, author or ISBN), display information about books, rate and review them, read other user's reviews, as well as get APIs - as per requirements.

Files within application:
  application.py contains code for application

  helpers.py defines additional functions:
                a) error function taking two arguments - error message and error code,
                b) login required route decoration

  import.py contains code allowing to import data to the database

  Templates:
    apology.html rendered when error occurs, displays error messages

    books.html displays information about a specific book, along with review/rating form and users reviews

    index.html is a homepage displaying a welcome message

    layout.html contains links to stylesheets, icon and scripts, a navbar (displaying Home, Search Database, Register and Log In for not logged in users and Home, Search Database and Log Out for logged in users) and a footer

    login.html is a template rendered when users take the login route (contains login form, consisting of fields for username and password)

    register.html is a template rendered when users take the route to register (contains registration form consisting of fields for username, e-mail, password and password confirmation)

    results.html is a template rendered after users perform a search - it displays a table with results ordered according to search method; titles within the table are links to specific books pages

    search.html is a template rendered after users take the search route - it contains a select list of 3 search methods (by isbn, title or author) and a submit button; it also contains a script managing the display of input field that matches chosen 'search by' value and enables button on input

  Static:
    book.ico is an icon for the application

    styles.css/styles.scss are stylesheets for the application

  Database holding the data contains 5 tables:
    users: id (primary key), username (varchar up to 32 chars), password (hashed, text), email (text)
    books: isbn (primary key), title, year
    people: id (primary key), name (text)
    authors: isbn, person_id
    reviews: user_id, isbn, review (varchar, up to 500 chars), rating (int), header (varchar, up to 32 chars), timestamp
