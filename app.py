from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Change to a random text if you want

DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create table if it does not exist
def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db()
    deals = conn.execute('SELECT * FROM deals ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', deals=deals)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            flash('Yay! You are logged in!', 'success')
            return redirect(url_for('admin'))
        else:
            error = 'Oops! Incorrect username or password.'
    return render_template('login.html', error=error)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        if title and price:
            conn = get_db()
            conn.execute('INSERT INTO deals (title, description, price) VALUES (?, ?, ?)',
                         (title, description, price))
            conn.commit()
            conn.close()
            flash('Deal added!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Title and Price are required!', 'error')
            
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out. Bye!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
