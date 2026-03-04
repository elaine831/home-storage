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

    c.execute('''
        CREATE TABLE IF NOT EXISTS shopping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

HOME_HTML = """
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
<a href="/add_to_shopping/{{item[1]}}">➕ 加入購物清單</a><br>
{% endif %}

<a href="/edit/{{item[0]}}">✏️ 修改</a> |
<a href="/delete/{{item[0]}}">🗑 刪除</a>
</div>
{% endfor %}

<hr>

<h3>🛒 購物清單</h3>
<form method="post" action="/add_shopping">
<input name="shopping_name" placeholder="手動加入商品" required>
<button type="submit">新增</button>
</form>

{% for s in shopping %}
<div style="border:1px solid #ddd;padding:8px;margin:5px 0;">
{{s[1]}}
<a href="/delete_shopping/{{s[0]}}">❌</a>
</div>
{% endfor %}
"""

EDIT_HTML = """
<!doctype html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<h2>✏️ 修改物品</h2>

<form method="post">
名稱:<br><input name="name" value="{{item[1]}}" required><br>
類別:<br><input name="category" value="{{item[2]}}" required><br>
數量:<br><input type="number" name="quantity" value="{{item[3]}}" required><br>
低庫存警戒:<br><input type="number" name="low_stock" value="{{item[4]}}" required><br>
到期日:<br><input type="date" name="expiry" value="{{item[5]}}" required><br><br>
<button type="submit">更新</button>
</form>

<br>
<a href="/">⬅ 返回首頁</a>
"""

@app.route("/")
def home():
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()

    c.execute("SELECT * FROM items ORDER BY expiry ASC")
    items = c.fetchall()

    c.execute("SELECT * FROM shopping")
    shopping = c.fetchall()

    conn.close()

    today = datetime.now()
    updated = []

    for item in items:
        expiry_date = datetime.strptime(item[5], "%Y-%m-%d")
        days_left = (expiry_date - today).days
        updated.append(item + (days_left,))

    return render_template_string(HOME_HTML, items=updated, shopping=shopping)

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

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()

    if request.method == "POST":
        c.execute("""
            UPDATE items
            SET name=?, category=?, quantity=?, low_stock=?, expiry=?
            WHERE id=?
        """, (
            request.form["name"],
            request.form["category"],
            request.form["quantity"],
            request.form["low_stock"],
            request.form["expiry"],
            item_id
        ))
        conn.commit()
        conn.close()
        return redirect("/")

    c.execute("SELECT * FROM items WHERE id=?", (item_id,))
    item = c.fetchone()
    conn.close()

    return render_template_string(EDIT_HTML, item=item)

@app.route("/delete/<int:item_id>")
def delete(item_id):
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()
    c.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/add_to_shopping/<name>")
def add_to_shopping(name):
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()
    c.execute("INSERT INTO shopping (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/add_shopping", methods=["POST"])
def add_shopping():
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()
    c.execute("INSERT INTO shopping (name) VALUES (?)", (request.form["shopping_name"],))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_shopping/<int:s_id>")
def delete_shopping(s_id):
    conn = sqlite3.connect("storage.db")
    c = conn.cursor()
    c.execute("DELETE FROM shopping WHERE id=?", (s_id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run()
