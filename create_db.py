from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

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

   def __init__(self, author, text):
       self.author = author
       self.text  = text

app.app_context().push()
db.create_all()
quotes = [QuoteModel('Народная мудрость', 'Нет пламя без огня'),
          QuoteModel('Rick Cook', 'Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.'),
          QuoteModel('Waldi Ravens', 'Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.'),
          QuoteModel('Moshers Law of Software Engineering', 'Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.'),
          QuoteModel('Yoggi Berra', 'В теории, теория и практика неразделимы. На практике это не так.'),
          QuoteModel('Test', 'Съешь еще этих французских булок, да выпей чаю')]

for quote in quotes:
    db.session.add(quote)
db.session.commit()
