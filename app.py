from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

CATEGORIES = ["生理用品", "食物類", "沐浴用品", "生活用品"]

def init_db():
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            quantity INTEGER,
            low_stock INTEGER,
            expiry TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

HTML = """
<!doctype html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<h2>📦 家庭物品管理</h2>

<h3>新增物品</h3>
<form method="post" action="/add">
名稱:<br><input name="name" required><br>

類別:<br>
<select name="category">
{% for c in categories %}
<option value="{{c}}">{{c}}</option>
{% endfor %}
</select><br>

數量:<br><input type="number" name="quantity" required><br>
低庫存警戒:<br><input type="number" name="low_stock" required><br>
到期日:<br><input type="date" name="expiry" required><br><br>

<button type="submit">新增</button>
</form>

<hr>

<h3>物品列表</h3>

{% for item in items %}
<div style="border:1px solid #ccc;padding:10px;margin:10px 0;">
<b>{{item["name"]}}</b><br>
類別: {{item["category"]}}<br>
數量: {{item["quantity"]}}<br>
到期日: {{item["expiry"]}}<br>
剩餘 {{item["days_left"]}} 天<br>

{% if item["low"] %}
<span style="color:red;">🔴 低庫存</span><br>
{% endif %}

{% if item["days_left"] <= 7 and item["days_left"] >= 0 %}
<span style="color:orange;">⚠️ 快過期</span><br>
{% endif %}

<a href="/delete/{{item['id']}}">🗑 刪除</a>
</div>
{% endfor %}
"""

@app.route("/")
def home():
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    rows = c.fetchall()
    conn.close()

    today = datetime.now()
    items = []

    for r in rows:
        expiry_date = datetime.strptime(r[5], "%Y-%m-%d")
        days_left = (expiry_date - today).days

        low = (r[3] <= r[4]) or (r[3] < 1)

        items.append({
            "id": r[0],
            "name": r[1],
            "category": r[2],
            "quantity": r[3],
            "low_stock": r[4],
            "expiry": r[5],
            "days_left": days_left,
            "low": low
        })

    # 排序邏輯
    items.sort(key=lambda x: (
        not x["low"],        # 低庫存排前面
        x["category"],       # 類別排序
        x["expiry"]          # 到期日排序
    ))

    return render_template_string(HTML, items=items, categories=CATEGORIES)

@app.route("/add", methods=["POST"])
def add():
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO items (name, category, quantity, low_stock, expiry)
        VALUES (?, ?, ?, ?, ?)
    """, (
        request.form["name"],
        request.form["category"],
        request.form["quantity"],
        request.form["low_stock"],
        request.form["expiry"]
    ))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:item_id>")
def delete(item_id):
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run()
