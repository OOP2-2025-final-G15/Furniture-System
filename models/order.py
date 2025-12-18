from peewee import Model, ForeignKeyField, DateTimeField, fn  # fnを追加
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
    def get_total_sales(cls):
        """総売り上げを計算して返す"""
        # OrderとProductを結合し、Product.priceの合計を出す
        query = cls.select(fn.SUM(Product.price)).join(Product)
        return query.scalar() or 0  # データがない場合は0を返す

    @classmethod
    def get_metrics(cls):
        """総売り上げ、客数、客単価をまとめて辞書で返す"""
        total_sales = cls.get_total_sales()
        
        # ユニークなユーザー数（購入客数）
        customer_count = cls.select(fn.COUNT(fn.DISTINCT(cls.user))).scalar() or 0
        
        # 客単価（総売り上げ ÷ 客数）
        avg_per_customer = 0
        if customer_count > 0:
            avg_per_customer = total_sales / customer_count
            
        return {
            "total_sales": int(total_sales),
            "customer_count": customer_count,
            "avg_per_customer": int(avg_per_customer)
        }