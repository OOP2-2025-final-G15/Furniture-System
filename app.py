
from flask import Flask, render_template,jsonify
from models import initialize_database,Order
from routes import blueprints
from peewee import *


app = Flask(__name__)

# データベースの初期化
initialize_database()

# 各Blueprintをアプリケーションに登録
for blueprint in blueprints:
    app.register_blueprint(blueprint)

# ホームページのルート
@app.route('/')
def index():
    gender_ratio = Order.get_gender_ratio()
    return render_template(
        'index.html',
        gender_ratio=gender_ratio
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
