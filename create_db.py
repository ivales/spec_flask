from sqlalchemy import Table, Integer, String, create_engine, inspect, Column, MetaData
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

BASE_DIR = Path(__file__).parent

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'test.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class QuoteModel(db.Model):
    id = db.Column(Integer, primary_key=True)
    author = db.Column(String(32), unique=False)
    text = db.Column(db.String(255), unique=False)
    rating = db.Column(db.Integer, unique=False, default=1)

    def __init__(self, author, text, rating):
        self.author = author
        self.text = text
        self.rating = rating


app.app_context().push()

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

engine = create_engine(f"sqlite:///{BASE_DIR / 'test.db'}")
if not inspect(engine).has_table("quote_model"):  # If table don't exist, Create.
    metadata = MetaData(engine)
    # Create a table with the appropriate Columns
    Table("quote_model", metadata,
          Column('id', Integer, primary_key=True, nullable=False),
          Column('author', String(32)), Column('text', String(255)),
          Column('rating', Integer))
    metadata.create_all()

if len(QuoteModel.query.all()) == 0:
    for quote in quotesForQuoteModel:
        db.session.add(quote)
    db.session.commit()
