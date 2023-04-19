import sqlite3

quotes = [
    ("Rick Cook","Программирование сегодня — это гонка разработчиков программ, стремящихся писать программы с большей и лучшей идиотоустойчивостью, и вселенной, которая пытается создать больше отборных идиотов. Пока вселенная побеждает."),
    ("Waldi Ravens","Программирование на С похоже на быстрые танцы на только что отполированном полу людей с острыми бритвами в руках."),
    ("Mosher's Law of Software Engineering","Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили."),
    ("Yoggi Berra","В теории, теория и практика неразделимы. На практике это не так.")

]

create_quote = "INSERT INTO quotes (author,text) VALUES (?, ?)"

# Подключение в БД
connection = sqlite3.connect("test.db")
# Создаем cursor, он позволяет делать SQL-запросы
cursor = connection.cursor()
# Выполняем запрос:
cursor.executemany(create_quote, quotes)
# Фиксируем выполнение(транзакцию)
connection.commit()
# Закрыть курсор:
cursor.close()
# Закрыть соединение:
connection.close()