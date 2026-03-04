from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

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
類別:<br><input name="category" required><br>
數量:<br><input type="number" name="quantity" required><br>
低庫存警戒:<br><input type="number" name="low_stock" required><br>
到期日:<br><input type="date" name="expiry" required><br><br>
<button type="submit">新增</button>
</form>

<hr>

<h3>物品列表</h3>
{% for item in items %}
<div style="border:1px solid #ccc;padding:10px;margin:10px 0;">
<b>{{item[1]}}</b><br>
類別: {{item[2]}}<br>
數量: {{item[3]}}<br>
到期日: {{item[5]}}<br>
剩餘 {{item[6]}} 天<br>

{% if item[6] <= 7 and item[6] >= 0 %}
<span style="color:red;">⚠️ 快過期</span><br>
{% endif %}

{% if item[3] <= item[4] %}
<span style="color:orange;">🔴 低庫存</span><br>
{% endif %}

<a href="/delete/{{item[0]}}">🗑 刪除</a>
</div>
{% endfor %}
"""

@app.route("/")
def home():
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()
    c.execute("SELECT * FROM items ORDER BY expiry ASC")
    items = c.fetchall()
    conn.close()

    today = datetime.now()
    updated = []

    for item in items:
        expiry_date = datetime.strptime(item[5], "%Y-%m-%d")
        days_left = (expiry_date - today).days
        updated.append(item + (days_left,))

    return render_template_string(HTML, items=updated)

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
