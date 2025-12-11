from flask import Blueprint, render_template, request, redirect, url_for
from models import Order, User, Product
from datetime import datetime
from peewee import fn  # 集計用

order_bp = Blueprint('order', __name__, url_prefix='/orders')

@order_bp.route('/')
def list():
    # 1. URLパラメータから 'month' を取得 (例: ?month=10)
    selected_month = request.args.get('month', type=int)

    # 2. ベースとなるクエリ（注文一覧）を作成
    # 結合(join)しておかないと、後でProductの価格を参照するときに非効率になるためjoinしておく
    query = Order.select().join(Product)

    # 3. 月が選択されていれば、その月でフィルタリング（絞り込み）
    if selected_month:
        # SQLiteの場合、日付から '月' を取り出すには strftime('%m', date_column) を使います
        # '{:02d}'.format(5) は '05' になります（DBの日付形式に合わせるため）
        query = query.where(fn.strftime('%m', Order.order_date) == '{:02d}'.format(selected_month))

    # 4. 絞り込まれたクエリを実行してリスト化（新しい順に並び替え）
    orders = query.order_by(Order.order_date.desc())

    # --- 集計処理 (月が選択されている場合のみ計算する設定にします) ---
    monthly_sales = None
    monthly_unit_price = None

    if selected_month:
        # 絞り込まれた 'query' を元に計算します
        
        # A. 総売上
        total_sales = query.select(fn.SUM(Product.price)).scalar() or 0
        
        # B. 客数（ユニークユーザー数）
        # join(User)しないと正確にUserをカウントできない場合があるため明示的にjoinしても良いが、
        # Order.user が外部キーなのでそのままカウント可能
        customer_count = query.select(fn.COUNT(fn.DISTINCT(Order.user))).scalar() or 0

        # C. 客単価
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
                           monthly_sales=monthly_sales,   # HTML側の変数名に合わせる
                           monthly_unit_price=monthly_unit_price) # HTML側の変数名に合わせる

# ... (add, edit 関数は変更なし) ...