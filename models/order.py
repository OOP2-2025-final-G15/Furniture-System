from peewee import Model, ForeignKeyField, DateTimeField, fn
from .db import db
from .user import User
from .product import Product

class Order(Model):
    user = ForeignKeyField(User, backref='orders')
    product = ForeignKeyField(Product, backref='orders')
    order_date = DateTimeField()

    class Meta:
        database = db

    @classmethod
    def get_gender_ratio(cls):
        query = (
            cls
            .select(User.gender, fn.COUNT(cls.id).alias('count'))
            .join(User)
            .group_by(User.gender)
        )

        result = {}
        for row in query:
            result[row.user.gender] = row.count

        return result