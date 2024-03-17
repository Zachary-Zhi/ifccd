import re

from flask import Flask, request
from flask_mongoalchemy import MongoAlchemy, BaseQuery

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['MONGOALCHEMY_DATABASE'] = 'ifccd'
db = MongoAlchemy(app)

class Author(db.Document):
    name = db.StringField()

class BookQuery(BaseQuery):

    def get_by_title(self, title):
        return self.filter({'title': title})


class Book(db.Document):
    query_class = BookQuery
    title = db.StringField()
    author = db.StringField()
    year = db.IntField()
    # def __init__(self, title, author, year):
    #     self.title = title
    #     self.author = author
    #     self.year = year

class BookObject(object):
    document_class = Book
    instance = None

    def __init__(self, title, author, year):
        super(BookObject, self).__init__()
        self.title = title
        self.author = author
        self.year = year
        print(self.title)
        print(self.author)
        print(self.year)

    def save(self):
        if self.instance is None:
            self.instance = self.document_class()
        self.instance.title = self.title
        self.instance.author = self.author
        self.instance.year = self.year
        print(self.title)
        print(self.author)
        print(self.year)
        self.instance.save()
        return self.instance

print("----------------")
# book1 = BookObject(title='shuxue1', author='tangjiafeng', year=2022)
# book1 = Book(title='zhengzhi', author='xutao', year=2022)
# book2 = Book(title='zhengzhi', author='xutao', year=2022)
# book3 = Book(title='yingyu', author='tianjing', year=2022)
# book1.save()
# book2.save()
# book3.save()
# print("saved :)")

tempbook = Book.query.get_by_title("shuxue")
print(tempbook.title)
print(tempbook.author)
print(tempbook.year)

print("over :)")




