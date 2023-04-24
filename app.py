from http.client import HTTPException
from flask_migrate import Migrate
from flask import Flask, jsonify, request
from pathlib import Path

import create_db
from create_db import QuoteModel, AuthorModel
from flask_sqlalchemy import SQLAlchemy

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'test.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = create_db.db
db.init_app(app)
migrate = Migrate(app, db)


@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


@app.route("/authors")
def get_authors():
    authors = []
    author_models = AuthorModel.query.all()
    for author_model in author_models:
        authors.append(authorModel_parse(author_model))
    return jsonify(authors), 200


@app.route("/authors/<int:author_id>")
def get_author_id(author_id):
    author_model = AuthorModel.query.get(author_id)
    if author_model is None:
        return f"Author with id={author_id} not found", 404
    return authorModel_parse(author_model)


@app.route("/authors", methods=['POST'])
def create_author():
    author_model = request.json
    if "name" in author_model:
        db.session.add(AuthorModel(author_model["name"]))
        db.session.commit()
        return "Author was successfully added", 201
    return "Data of new author is incorrect, should contain \"name\" parameter"


@app.route("/authors/<int:author_id>", methods=['PUT'])
def edit_author(author_id):
    author_model = AuthorModel.query.get(author_id)
    if author_model is None:
        return f"Author with id={author_id} not found"
    new_author = request.json
    if "name" in new_author:
        author_model.name = new_author["name"]
        db.session.commit()
        return f"Author with id={author_id} was updated", 200
    return f"It is nothing to update"


@app.route("/authors/<int:author_id>", methods=['DELETE'])
def delete_author(author_id):
    author_model = AuthorModel.query.get(author_id)
    if author_model is None:
        return f"Author with id={author_id} not found", 404
    db.session.delete(author_model)
    db.session.commit()
    return f"Author with id={author_id} and his quotes was successfully deleted", 200


@app.route("/quotes/")
def get_quotes():
    quotes = []
    quote_models = QuoteModel.query.all()
    for quote_model in quote_models:
        quotes.append(quoteModel_parse(quote_model))
    return quotes


@app.route("/quotes/<int:quote_id>")
def get_quote_id(quote_id):
    quote_model = QuoteModel.query.get(quote_id)
    if quote_model is None:
        return f"Quote with id={quote_id} not found", 404
    return quoteModel_parse(quote_model)


@app.route("/authors/<int:author_id>/quotes")
def get_quote_by_author_id(author_id):
    author = get_author_id(author_id)
    if isinstance(author, tuple):
        return author
    quotes = get_quotes()
    authors_quote = []
    for quote in quotes:
        if quote["author"] == author["name"]:
            authors_quote.append(quote)
    return authors_quote


@app.route("/authors/<int:author_id>/quotes", methods=['POST'])
def create_quote(author_id):
    author = get_author_id(author_id)
    if isinstance(author, tuple):
        return author
    new_qoute = request.json
    error = "Data of new quote is incorrect, should contain only \"text\" (string) and \"rating\" (int 1..5)" \
            " parameters"
    print(new_qoute)
    try:
        if not isinstance(new_qoute["text"], str) or not isinstance(new_qoute["rating"], int) or not 1 <= \
                                                                                                     new_qoute[
                                                                                                         "rating"] <= 5:
            return error
        else:
            db.session.add(QuoteModel(AuthorModel.query.get(author_id), new_qoute["text"], new_qoute["rating"]))
            db.session.commit()
    except TypeError:
        return error
    return "Quote was successfully added", 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    count = 0
    quote_model = QuoteModel.query.get(quote_id)
    if quote_model is None:
        return f"Quote with id={quote_id} not found", 404
    new_quote = request.json
    if "author_id" in new_quote and isinstance(new_quote["author_id"], int) and AuthorModel.query.get(new_quote["author_id"]) is not None:
        quote_model.author_id = new_quote["author_id"]
        count += 1
    if "text" in new_quote:
        quote_model.text = new_quote["text"]
        count += 1
    if "rating" in new_quote and isinstance(new_quote["rating"], int) and 1 <= new_quote["rating"] <= 5:
        quote_model.rating = new_quote["rating"]
        count += 1
    if count == 0:
        return f"It is nothing to update"
    db.session.commit()
    return f"Quote with id={quote_id} was updated", 200


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id):
    quote_model = QuoteModel.query.get(quote_id)
    if quote_model is None:
        return f"Quote with id={quote_id} not found", 404
    db.session.delete(quote_model)
    db.session.commit()
    return f"Quote with id={quote_id} was successfully deleted", 200


@app.route("/quotes/filter", methods=['GET'])
def filter_quote():
    args = request.args
    if "author" not in args and "rating" not in args:
        return "Filter parameters are absent or incorrect"
    author = args.get('author')
    rating = args.get('rating')
    if None not in (author, rating):
        quoteModels = QuoteModel.query.filter_by(author=author, rating=rating).all()
    elif author is not None:
        quoteModels = QuoteModel.query.filter_by(author=author).all()
    elif rating is not None:
        quoteModels = QuoteModel.query.filter_by(rating=rating).all()
    filter_quotes = []
    for quoteModel in quoteModels:
        filter_quotes.append(quoteModel_parse(quoteModel))
    if not filter_quotes:
        return 'There is no result for your request', 404
    return jsonify(filter_quotes), 200


def quoteModel_parse(quoteModel):
    quote = {"id": quoteModel.id, "author": authorModel_parse(AuthorModel.query.get(quoteModel.author_id))["name"],
             "text": quoteModel.text, "rating": quoteModel.rating}
    return quote


def authorModel_parse(authorModel):
    author = {"id": authorModel.id, "name": authorModel.name}
    return author


if __name__ == "__main__":
    app.run(debug=True)
