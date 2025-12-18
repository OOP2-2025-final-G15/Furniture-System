from peewee import Model, CharField, IntegerField
from .db import db

class User(Model):
    name = CharField()
    age = IntegerField()
    gender = CharField() 

    class Meta:
        database = db