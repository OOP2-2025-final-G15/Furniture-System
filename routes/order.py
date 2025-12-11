from flask import Blueprint, render_template, request, redirect, url_for
from models import Order, User, Product
from datetime import datetime # 他のBlueprintのインポート例
from peewee import fn  # 集計関数 fn を追加

# Blueprintの作成
order_bp = Blueprint('order', __name__, url_prefix='/orders')


@order_bp.route('/')
def list():
    orders = Order.select()
    # 1. 総売り上げ (OrderとProductを結合して価格を合計)
    # Productモデルに price カラムがある前提です
    query_sales = Order.select(fn.SUM(Product.price)).join(Product)
    total_sales = query_sales.scalar() or 0

    # 2. 客数 (ユニークなUser数をカウント)
    query_customers = Order.select(fn.COUNT(fn.DISTINCT(Order.user)))
    customer_count = query_customers.scalar() or 0

    # 3. 客単価 (割り算)
    if customer_count > 0:
        avg_per_customer = int(total_sales / customer_count)
    else:
        avg_per_customer = 0
    return render_template('order_list.html', 
                           title='注文一覧', 
                           items=orders,
                            total_sales=total_sales,
                            customer_count=customer_count, 
                            avg_per_customer=avg_per_customer)


@order_bp.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        user_id = request.form['user_id']
        product_id = request.form['product_id']
        order_date = datetime.now()
        Order.create(user=user_id, product=product_id, order_date=order_date)
        return redirect(url_for('order.list'))
    
    users = User.select()
    products = Product.select()
    return render_template('order_add.html', users=users, products=products)


@order_bp.route('/edit/<int:order_id>', methods=['GET', 'POST'])
def edit(order_id):
    order = Order.get_or_none(Order.id == order_id)
    if not order:
        return redirect(url_for('order.list'))

    if request.method == 'POST':
        order.user = request.form['user_id']
        order.product = request.form['product_id']
        order.save()
        return redirect(url_for('order.list'))

    users = User.select()
    products = Product.select()
    return render_template('order_edit.html', order=order, users=users, products=products)
