from flask import Flask, render_template, request, redirect, url_for
import sqlite3

DB_NAME = "membership.db"  # 資料庫名稱


def connect_db():
    conn = sqlite3.connect(DB_NAME)  # 連接到 SQLite 資料庫
    conn.row_factory = sqlite3.Row  # 設定 row_factory 以便使用字典方式存取資料
    return conn


with connect_db() as conn:
    cursor = conn.cursor()
    try:
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
    except sqlite3.Error as error:
        print(f"執行資料庫操作時發生錯誤：{error}")

app = Flask(__name__)  # __name__ 代表目前執行的模組


@app.template_filter('add_stars')
def add_stars(s: str) -> str:
    return f'★{s}★'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        birthdate = request.form.get('birthdate')
        if not username or not email or not password:
            return render_template('error.html', error_message='請輸入用戶名、電子郵件和密碼')
        with connect_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT * FROM members WHERE username = ?", (username,))
                for row in cursor:
                    if row['username'] == username:
                        return render_template('error.html', error_message='用戶名已存在')
                cursor.execute(
                    "INSERT INTO members "
                    "(username, email, password, phone, birthdate) VALUES (?, ?, ?, ?, ?)",
                    (username, email, password, phone, birthdate)
                )
                conn.commit()
            except sqlite3.Error as error:
                print(f"執行資料庫操作時發生錯誤：{error}")
                return render_template('error.html', error_message='請輸入用戶名、電子郵件和密碼')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            return render_template('error.html', error_message='請輸入電子郵件和密碼')
        with connect_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT * FROM members WHERE email = ? AND password = ?", (email, password))
                for row in cursor:
                    if row['email'] == email and row['password'] == password:
                        return redirect(url_for('welcome', iid=row['iid']))
                return render_template('error.html', error_message='電子郵件或密碼錯誤')
            except sqlite3.Error as error:
                print(f"執行資料庫操作時發生錯誤：{error}")
                return render_template('error.html', error_message='電子郵件或密碼錯誤')
    return render_template('login.html')


@app.route('/welcome/<int:iid>')
def welcome(iid: int):
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM members WHERE iid = ?", (iid,))
            for row in cursor:
                if row['iid'] == iid:
                    user = row
                    return render_template('welcome.html', user=user)
            return render_template('error.html', error_message='用戶不存在')

        except sqlite3.Error as error:
            print(f"執行資料庫操作時發生錯誤：{error}")
            return render_template('error.html', error_message='資料庫錯誤')


@app.route('/edit_profile/<int:iid>', methods=['GET', 'POST'])
def edit_profile(iid: int):
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        birthdate = request.form.get('birthdate')
        if not iid:
            return redirect(url_for('index'))
        if not email or not password:
            return render_template('error.html', error_message='請輸入電子郵件和密碼')
        with connect_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT * FROM members WHERE email = ?", (email,))
                for row in cursor:
                    if row['email'] == email:
                        return render_template('error.html', error_message='電子郵件已被使用')
                else:
                    cursor.execute(
                        "UPDATE members SET email = ?, password = ?, phone = ?, birthdate = ? WHERE iid = ?",
                        (email, password, phone, birthdate, iid)
                    )
                    conn.commit()
                    return redirect(url_for('welcome', iid=iid))
            except sqlite3.Error as error:
                print(f"執行資料庫操作時發生錯誤：{error}")
                return render_template('error.html', error_message='請輸入電子郵件和密碼')

    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM members WHERE iid = ?", (iid,))
            for row in cursor:
                if row['iid'] == iid:
                    user = row
                    return render_template('edit_profile.html', user=user)
            return render_template('error.html', error_message='用戶不存在')
        except sqlite3.Error as error:
            print(f"執行資料庫操作時發生錯誤：{error}")
            return render_template('error.html', error_message='資料庫錯誤')


@app.route('/delete/<int:iid>')
def delete_user(iid: int):
    with connect_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM members WHERE iid = ?", (iid,))
            conn.commit()
        except sqlite3.Error as error:
            print(f"執行資料庫操作時發生錯誤：{error}")
            return render_template('error.html', error_message='刪除用戶失敗')
    return redirect(url_for('index'))
