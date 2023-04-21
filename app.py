from http.client import HTTPException

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

# from create_db import QuoteModel

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'test.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(32), unique=False)
    text = db.Column(db.String(255), unique=False)
    rating = db.Column(db.Integer, unique=False, default=1)

    def __init__(self, author, text, rating):
        self.author = author
        self.text = text
        self.rating = rating


app.app_context().push()
db.drop_all()
db.create_all()
quotesForQuoteModel = [QuoteModel('Народная мудрость', 'Нет пламя без огня', 1),
                       QuoteModel('Rick Cook',
                                  'Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.',
                                  4),
                       QuoteModel('Waldi Ravens',
                                  'Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.',
                                  1),
                       QuoteModel('Moshers Law of Software Engineering',
                                  'Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.', 3),
                       QuoteModel('Yoggi Berra', 'В теории, теория и практика неразделимы. На практике это не так.', 2),
                       QuoteModel('Test', 'Съешь еще этих французских булок, да выпей чаю', 5)]

for quote in quotesForQuoteModel:
    db.session.add(quote)
db.session.commit()


@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


@app.route("/quotes/")
def get_quotes():
    quotes = []
    quoteModels = QuoteModel.query.all()
    for quoteModel in quoteModels:
        quotes.append(quoteModel_parse(quoteModel))
    return jsonify(quotes), 201


@app.route("/quotes/<int:quote_id>")
def get_quote_id(quote_id):
    quoteModel = QuoteModel.query.get(quote_id)
    if quoteModel is None:
        return f"Quote with id={quote_id} not found", 404
    return jsonify(quoteModel_parse(quoteModel)), 201


@app.route("/quotes", methods=['POST'])
def create_quote():
    db.session.add(QuoteModel(*tuple(request.json.values())))
    db.session.commit()
    return "Quote was successfully added", 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    quoteModel = QuoteModel.query.get(quote_id)
    if quoteModel is None:
        return f"Quote with id={quote_id} not found", 404
    new_quote = request.json
    if "author" in new_quote and "text" in new_quote and "rating" in new_quote:
        quoteModel.author = new_quote["author"]
        quoteModel.text = new_quote["text"]
        quoteModel.rating = new_quote["rating"]
    elif "author" in new_quote and "text" in new_quote:
        quoteModel.author = new_quote["author"]
        quoteModel.text = new_quote["text"]
    elif "author" in new_quote and "rating" in new_quote:
        quoteModel.text = new_quote["author"]
        quoteModel.rating = new_quote["rating"]
    elif "text" in new_quote and "rating" in new_quote:
        quoteModel.text = new_quote["text"]
        quoteModel.rating = new_quote["rating"]
    elif "author" in new_quote:
        quoteModel.rating = new_quote["author"]
    elif "text" in new_quote:
        quoteModel.rating = new_quote["text"]
    elif "rating" in new_quote:
        quoteModel.rating = new_quote["rating"]
    else:
        return "It is nothing to update"
    db.session.commit()
    return f"Quote with id={quote_id} was updated", 200


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id):
    quoteModel = QuoteModel.query.get(quote_id)
    if quoteModel is None:
        return f"Quote with id={quote_id} not found", 404
    db.session.delete(quoteModel)
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
