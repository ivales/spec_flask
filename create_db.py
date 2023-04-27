from sqlalchemy import Table, Integer, String, create_engine, inspect, Column, MetaData, func, DateTime
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


class AuthorModel(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic',  cascade="all, delete-orphan")

    def __init__(self, name):
        self.name = name


class QuoteModel(db.Model):
    __tablename__ = "quotes"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)
    rating = db.Column(db.Integer, unique=False, default=1)
    created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __init__(self, author, text, rating=1):
        self.author_id = author.id
        self.text = text
        self.rating = rating


app.app_context().push()


authorsForAuthorModel = [AuthorModel('Nick'), AuthorModel('Folk'), AuthorModel('Tom'), AuthorModel('Ralph'), AuthorModel('Emerson')]


engine = create_engine(f"sqlite:///{BASE_DIR / 'test.db'}")


if not inspect(engine).has_table("authors"):
    metadata = MetaData(engine)
    Table("authors", metadata,
          Column('id', Integer, primary_key=True, nullable=False),
          Column('name', String(32)))
    metadata.create_all()


if not inspect(engine).has_table("quotes"):  # If table don't exist, Create.
    metadata = MetaData(engine)
    # Create a table with the appropriate Columns
    Table("quotes", metadata,
          Column('id', Integer, primary_key=True, nullable=False),
          Column('author_id', Integer), Column('text', String(255)),
          Column('rating', Integer, nullable=False, default=1),
          Column('created', DateTime(timezone=True), server_default=func.now())
          )
    metadata.create_all()


if len(AuthorModel.query.all()) == 0:
    for author in authorsForAuthorModel:
        db.session.add(author)
    db.session.commit()

quotesForQuoteModel = [QuoteModel(AuthorModel.query.get(1), 'Нет пламя без огня'),
                       QuoteModel(AuthorModel.query.get(1),
                                  'Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает.',
                                  4),
                       QuoteModel(AuthorModel.query.get(2),
                                  'Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках.',
                                  1),
                       QuoteModel(AuthorModel.query.get(3),
                                  'Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.', 3),
                       QuoteModel(AuthorModel.query.get(4), 'В теории, теория и практика неразделимы. На практике это не так.', 2),
                       QuoteModel(AuthorModel.query.get(5), 'Съешь еще этих французских булок, да выпей чаю', 5)]


if len(QuoteModel.query.all()) == 0:
    for quote in quotesForQuoteModel:
        db.session.add(quote)
    db.session.commit()
