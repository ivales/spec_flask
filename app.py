import random

from flask import Flask, request

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


quotes = [
   {
       "id": 3,
       "author": "Rick Cook",
       "text": "Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."
   },
   {
       "id": 5,
       "author": "Waldi Ravens",
       "text": "Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."
   },
   {
       "id": 6,
       "author": "Mosher's Law of Software Engineering",
       "text": "Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."
   },
   {
       "id": 8,
       "author": "Yoggi Berra",
       "text": "В теории, теория и практика неразделимы. На практике это не так."
   },

]
#Task 1-1
@app.route("/quotes/<int:id>")
def get_quote(id):
    for quote in quotes:
        if quote["id"] == id:
            return quote
#Task 1-2
    return f"Quote with id={id} not found", 404

#Task1-3
@app.route("/quotes/count")
def count_quotes():
    return {
            "count":len(quotes)
            }, 200

#Task1-4
@app.route("/quotes/random")
def random_quote():
    return random.choice(quotes), 200

#Task2-1
@app.route("/quotes", methods=['POST'])
def create_quote():
   data = request.json
   data['id'] = last_quote_id() + 1
   quotes.append(data)
#Task2-2
   return data, 201

#Task 2-4
@app.route("/quotes/<int:id>", methods=['PUT'])
def edit_quote(id):
    for i in range(len(quotes)):
        if quotes[i]["id"] == id:
            quotes[i].update(request.json)
            return quotes[i], 200
    return f"Quote with id={id} not found", 404

#Task 2-5
@app.route("/quotes/<int:id>", methods=['DELETE'])
def delete_quote(id):
    for quote in quotes:
        if quote["id"] == id:
            quotes.remove(quote)
            return f"Quote with id={id} is deleted", 200
    return f"Quote with id={id} not found", 404


def last_quote_id():
    return quotes[-1]['id']

if __name__ == "__main__":
   app.run(debug=True)