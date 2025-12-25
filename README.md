# アプリ名: Furniture-System

概要:

家具販売を想定した、ユーザー、製品、注文のデータ登録を行う簡易アプリケーション

Flask と Peeweeを用いて開発されており、注文データをもとに 売上の集計を行うことができます。

製品別売上（棒グラフ）と、注文全体の男女比（円グラフ）をトップページに表示することで、管理者が売上状況を一目で把握できるようにしています。


## アピールポイント
![Furniture-System デモ](furniture.gif)

## 動作条件: require

> 動作に必要な条件を書いてください。

```bash
python 3.13 or higher

# python lib
Flask==3.0.3
peewee==3.17.7
```

## 使い方: usage

> このリポジトリのアプリを動作させるために行う手順を詳細に書いてください。

```bash
$ python app.py
# Try accessing "http://localhost:8080" in your browser.
```
