from flask import Flask, session, render_template, jsonify, request, url_for, flash, redirect
from flask_session import Session
from tempfile import mkdtemp
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = os.getenv("SECRET_KEY")
db.init_app(app)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    if (request.method == "GET"):
        name = request.args.get("name")
        if not name:
            return redirect("/")
    else:
        name = request.form.get("name")    
    authors = Authors.query.with_entities(Authors.id,Authors.author).filter(Authors.author.ilike("%{}%".format(name))).all()
    books = Books.query.with_entities(Books.id,Books.book_name,Books.author_id).filter(Books.book_name.ilike("%{}%".format(name))).all()
    session["authors"] = authors
    session["books"] = books
    if not session["authors"] and not session["books"]:
        flash("oops: Nothing found on this query")
        return redirect("/")
    elif session["authors"] and not session["books"]:
        flash("oops: NO books found")
    else:
        flash("oops: No authors found")
    return render_template("search.html")

@app.route("/authors/<int:author_id>")
def authors(author_id):
    books = Books.query.with_entities(Books.book_name, Books.year).filter_by(author_id=author_id).order_by(Books.year.asc()).all()
    if (books == []):
        flash("oops: No author found!")
        return redirect("/")
    return render_template("authors.html", books=books)

@app.route("/books/<int:book_id>")
def books(book_id):
    detail = Books.query.with_entities(Books.id, Books.isbn, Books.book_name, Books.year, Books.author_id).filter_by(id=book_id).first()
    author_detail = Authors.query.with_entities(Authors.author).filter_by(id=detail.author_id).first()
    if not detail:
        flash("oops: No book found!")
        return redirect("/")
    return render_template("books.html" , detail=detail, author_detail=author_detail)
