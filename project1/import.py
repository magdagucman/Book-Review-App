import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

f = open("books.csv")
reader = csv.reader(f)

counter = 0
for isbn, title, author, year in reader:
    if counter == 0:
        counter +=1
    else:
        db.execute("INSERT INTO books (isbn, title, year) VALUES (:isbn, :title, :year)", {"isbn": isbn, "title": title, "year": year})
        rows = db.execute("SELECT * FROM people WHERE name = :author", {"author": author}).fetchall()

        # Ensure author's name enters the database only once
        if len(rows) == 0:
            db.execute("INSERT INTO people (name) VALUES (:author)", {"author": author})

        rows = db.execute("SELECT * FROM people WHERE name = :author", {"author": author}).fetchone()
        person_id = rows['id']
        db.execute("INSERT INTO authors (isbn, person_id) VALUES (:isbn, :person_id)", {"isbn": isbn, "person_id": person_id})
db.commit()
