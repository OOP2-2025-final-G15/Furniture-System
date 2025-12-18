from flask import Blueprint, render_template, request, redirect, url_for
from models import Order, User, Product
from datetime import datetime
from peewee import fn  # 集計用関数

# Blueprintの作成
order_bp = Blueprint('order', __name__, url_prefix='/orders')

@order_bp.route('/')
def list():
    # 1. URLパラメータから 'month' を取得 (例: ?month=10)
    selected_month = request.args.get('month', type=int)

    # 2. ベースとなるクエリを作成
    # Productの価格(price)を集計に使うため、あらかじめ結合(join)しておく
    query = Order.select().join(Product)

    # 3. 月が選択されていれば、その月でフィルタリング（絞り込み）
    if selected_month:
        # SQLiteの場合、日付から '月' を取り出すには strftime('%m', date_column) を使います
        # '{:02d}'.format(5) は '05' になります（DBの日付形式に合わせるため）
        query = query.where(fn.strftime('%m', Order.order_date) == '{:02d}'.format(selected_month))

    # 4. 表示用データの取得（新しい順に並び替え）
    orders = query.order_by(Order.order_date.desc())

    # --- 集計処理 ---
    monthly_sales = None
    monthly_unit_price = None

    # 月が選択されている場合のみ計算を実行
    if selected_month:
        # A. 総売上 (Product.price の合計)
        total_sales = query.select(fn.SUM(Product.price)).scalar() or 0
        
        # B. 客数（ユニークユーザー数）
        customer_count = query.select(fn.COUNT(fn.DISTINCT(Order.user))).scalar() or 0

        # C. 客単価 (売上 ÷ 客数)
        if customer_count > 0:
            avg_price = int(total_sales / customer_count)
        else:
            avg_price = 0

        # テンプレートに渡す変数にセット
        monthly_sales = total_sales
        monthly_unit_price = avg_price

    return render_template('order_list.html', 
                           title='注文一覧', 
                           items=orders,
                           selected_month=selected_month, # プルダウンの選択状態維持用
                           monthly_sales=monthly_sales,   # HTML表示用
                           monthly_unit_price=monthly_unit_price) # HTML表示用


@order_bp.route('/add', methods=['GET', 'POST'])
def add():
    # POSTリクエスト（フォーム送信時）
    if request.method == 'POST':
        user_id = request.form['user_id']
        product_id = request.form['product_id']
        # フォームから年/月/日を受け取って日時を作成（より厳密に検証）
        y_raw = request.form.get('year', '').strip()
        m_raw = request.form.get('month', '').strip()
        d_raw = request.form.get('day', '').strip()
        order_date = None
        if y_raw.isdigit() and m_raw.isdigit() and d_raw.isdigit():
            try:
                year = int(y_raw)
                month = int(m_raw)
                day = int(d_raw)
                order_date = datetime(year, month, day)
            except ValueError:
                order_date = None

        # 無効な入力の場合は現在日時を使用
        if order_date is None:
            # 存在しない日付などの入力はエラーとしてフォームに戻す
            users = User.select()
            products = Product.select()
            now = datetime.now()
            years = range(now.year - 10, now.year + 11)
            months = range(1, 13)
            days = range(1, 32)
            error = '無効な日付です。正しい日付を指定してください。'
            return render_template('order_add.html', users=users, products=products,
                                   years=years, months=months, days=days,
                                   default_year=now.year, default_month=now.month, default_day=now.day,
                                   selected_year=y_raw, selected_month=m_raw, selected_day=d_raw,
                                   error=error)

        # データの保存
        Order.create(user=user_id, product=product_id, order_date=order_date)
        return redirect(url_for('order.list'))
    
    # GETリクエスト（画面表示時）
    users = User.select()
    products = Product.select()
    # 年/月/日のプルダウンを作るための情報を渡す
    now = datetime.now()
    years = range(now.year - 10, now.year + 11)  # 過去10年〜未来10年
    months = range(1, 13)
    days = range(1, 32)
    return render_template('order_add.html', users=users, products=products,
                           years=years, months=months, days=days,
                           default_year=now.year, default_month=now.month, default_day=now.day)


@order_bp.route('/edit/<int:order_id>', methods=['GET', 'POST'])
def edit(order_id):
    # 編集対象の注文を取得（なければ一覧に戻る）
    order = Order.get_or_none(Order.id == order_id)
    if not order:
        return redirect(url_for('order.list'))

    # POSTリクエスト（更新処理）
    if request.method == 'POST':
        order.user = request.form['user_id']
        order.product = request.form['product_id']
        # 日付が送られていれば更新（厳密に検証）
        y_raw = request.form.get('year', '').strip()
        m_raw = request.form.get('month', '').strip()
        d_raw = request.form.get('day', '').strip()
        if y_raw.isdigit() and m_raw.isdigit() and d_raw.isdigit():
            try:
                year = int(y_raw)
                month = int(m_raw)
                day = int(d_raw)
                order.order_date = datetime(year, month, day)
            except ValueError:
                # 無効な日付ならエラーを返して編集画面に戻す
                users = User.select()
                products = Product.select()
                now = datetime.now()
                years = range(now.year - 10, now.year + 11)
                months = range(1, 13)
                days = range(1, 32)
                error = '無効な日付です。正しい日付を指定してください。'
                return render_template('order_edit.html', order=order, users=users, products=products,
                                       years=years, months=months, days=days,
                                       selected_year=y_raw, selected_month=m_raw, selected_day=d_raw,
                                       error=error)
        order.save() # 変更を保存
        return redirect(url_for('order.list'))

    # GETリクエスト（編集画面表示）
    users = User.select()
    products = Product.select()

    # 年/月/日のプルダウンを作るための情報を渡す
    now = datetime.now()
    years = range(now.year - 10, now.year + 11)
    months = range(1, 13)
    days = range(1, 32)
    return render_template('order_edit.html', order=order, users=users, products=products,
                           years=years, months=months, days=days)
