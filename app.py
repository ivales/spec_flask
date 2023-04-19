import random
import sqlite3
from pathlib import Path
from flask import Flask, request, jsonify, g

BASE_DIR = Path(__file__).parent
path_to_db = BASE_DIR / "test.db"

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(path_to_db)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/quotes/")
def get_quotes():
    cursor = get_db().cursor()
    cursor.execute("SELECT * from quotes")
    quotes = cursor.fetchall()
    return jsonify(quotes), 201


@app.route("/quotes/<int:quote_id>")
def get_quote(quote_id):
    cursor = get_db().cursor()
    cursor.execute(f"SELECT * from quotes WHERE id={quote_id}")
    quote = cursor.fetchone()
    if quote is None:
        return f"Quote with id={quote_id} not found", 404
    return jsonify(quote)


@app.route("/quotes", methods=['POST'])
def create_quote():
    quote = request.json
    cursor = get_db().cursor()
    cursor.execute("INSERT INTO quotes (author,text) VALUES (?, ?)", (quote["author"], quote["text"]))
    get_db().commit()
    return "Quote was successfully added", 201


@app.route("/quotes/<int:quote_id>", methods=['PUT'])
def edit_quote(quote_id):
    cursor = get_db().cursor()
    command = quote_update(request.json, quote_id)
    if command is None:
        return f"It is nothing to update"
    cursor.execute(command)
    get_db().commit()
    if cursor.rowcount == 0:
        return f"Quote with id={quote_id} not found", 404
    return f"Quote with id={quote_id} was updated", 200


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete_quote(quote_id):
    cursor = get_db().cursor()
    cursor.execute(f"DELETE from quotes WHERE id={quote_id}")
    get_db().commit()
    if cursor.rowcount > 0:
        return f"Quote with id={quote_id} deleted", 200
    return f"Quote with id={quote_id} not found", 404


def quote_update(quote, quote_id):
    if "author" in quote and "text" in quote:
        return f"UPDATE quotes SET author='{quote['author']}',text='{quote['text']}' WHERE id={quote_id}"
    elif "author" in quote:
        return f"UPDATE quotes SET author='{quote['author']}' WHERE id={quote_id}"
    elif "text" in quote:
        return f"UPDATE quotes SET text='{quote['text']}' WHERE id={quote_id}"
    else:
        return None


if __name__ == "__main__":
    app.run(debug=True)
