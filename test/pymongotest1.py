import os

from flask import Flask
import datetime
import pymongo
class DBUser(db.Document):
    email = db.EmailField(unique=True)
    password = db.StringField(default=True)
    active = db.BooleanField(default=True)
    isAdmin = db.BooleanField(default=False)
    timestamp = db.DateTimeField(default=datetime.datetime.now())


class User():
    def __init__(self, email=None, password=None, active=True, id=None):
        self.email = email
        self.password = password
        self.active = active
        self.isAdmin = False
        self.id = None

    def save(self):
        newUser = DBUser(email=self.email, password=self.password, active=self.active)
        newUser.save()
        print
        "new user id = %s " % newUser.id
        self.id = newUser.id
        return self.id

    def get_by_email(self, email):

        dbUser = DBUser.objects.get(email=email)
        if dbUser:
            self.email = dbUser.email
            self.active = dbUser.active
            self.id = dbUser.id
            return self
        else:
            return None

    def get_by_email_w_password(self, email):

        try:
            dbUser = DBUser.objects.get(email=email)

            if dbUser:
                self.email = dbUser.email
                self.active = dbUser.active
                self.password = dbUser.password
                self.id = dbUser.id
                return self
            else:
                return None
        except:
            print
            "there was an error"
            return None

    def get_mongo_doc(self):
        if self.id:
            return DBUser.objects.with_id(self.id)
        else:
            return None

    def get_by_id(self, id):
        dbUser = DBUser.objects.with_id(id)
        if dbUser:
            self.email = dbUser.email
            self.active = dbUser.active
            self.id = dbUser.id

            return self
        else:
            return None


user = User("email", "password_hash")
print(user)
user.save()

