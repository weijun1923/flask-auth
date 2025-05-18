from flask import Flask, request, jsonify, render_template
import sqlite3

DB_NAME = "membership.db"  # 資料庫名稱


def connect_db():
    conn = sqlite3.connect(DB_NAME)  # 連接到 SQLite 資料庫
    conn.row_factory = sqlite3.Row  # 設定 row_factory 以便使用字典方式存取資料
    return conn


with connect_db() as conn:
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS members (
        iid INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        phone TEXT,
        birthdate TEXT
    )   
        """
    )
    cursor.execute(
        "INSERT OR IGNORE INTO members (username, email, password, phone, birthdate)"
        " VALUES (?, ?, ?, ?, ?)",
        ('admin', 'admin@example.com', 'admin123', '0912345678', '1990-01-01')
    )
    conn.commit()  # 提交變更


app = Flask(__name__)  # __name__ 代表目前執行的模組


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")
