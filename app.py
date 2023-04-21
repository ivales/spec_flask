import create_db
from http.client import HTTPException
from flask import Flask, jsonify, request
from pathlib import Path
from create_db import QuoteModel

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'test.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = create_db.db
db.init_app(app)


@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


@app.route("/quotes/")
def get_quotes():
    quotes = []
    quote_models = QuoteModel.query.all()
    for quote_model in quote_models:
        quotes.append(quoteModel_parse(quote_model))
    return jsonify(quotes), 200


@app.route("/quotes/<int:quote_id>")
def get_quote_id(quote_id):
    quote_model = QuoteModel.query.get(quote_id)
    if quote_model is None:
        return f"Quote with id={quote_id} not found", 404
    return jsonify(quoteModel_parse(quote_model)), 200


@app.route("/quotes", methods=['POST'])
def create_quote():
    db.session.add(QuoteModel(*tuple(request.json.values())))
    db.session.commit()
    return "Quote was successfully added", 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    count = 0
    quote_model = QuoteModel.query.get(quote_id)
    if quote_model is None:
        return f"Quote with id={quote_id} not found", 404
    new_quote = request.json
    if "author" in new_quote:
        quote_model.author = new_quote["author"]
        count += 1
    if "text" in new_quote:
        quote_model.text = new_quote["text"]
        count += 1
    if "rating" in new_quote:
        quote_model.rating = new_quote["rating"] if 1 <= new_quote["rating"] <= 5 else 1
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
    quote = {"id": quoteModel.id, "author": quoteModel.author, "text": quoteModel.text, "rating": quoteModel.rating}
    return quote


if __name__ == "__main__":
    app.run(debug=True)
