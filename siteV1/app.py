from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'])
    return None

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (form.username.data,)).fetchone()
        if user and check_password_hash(user['password_hash'], form.password.data):
            user_obj = User(user['id'], user['username'])
            login_user(user_obj)
            return redirect(url_for('index'))
        flash('Invalid username or password')
        conn.close()
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (form.username.data, form.email.data)).fetchone()
        if user:
            flash('Username or email already exists! Please try another one or login.')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data)
        conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', 
                     (form.username.data, form.email.data, hashed_password))
        conn.commit()
        conn.close()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        payment = request.form['payment']
        cart_items_json = request.form['cart_items']

        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO orders (name, email, address, payment) VALUES (?, ?, ?, ?)', 
                        (name, email, address, payment))
            order_id = cur.lastrowid
            cart_items = json.loads(cart_items_json)
            for item in cart_items:
                cur.execute('INSERT INTO order_items (order_id, product_name, quantity) VALUES (?, ?, ?)', 
                            (order_id, item['name'], item['quantity']))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('checkout.html')

@app.route('/product/<int:product_id>')
def product(product_id):
    with get_db_connection() as conn:
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        if not product:
            return 'Product not found', 404
    return render_template('product.html', product_name=product['name'], product_description=product['description'], product_price=product['price'], product_image=product['image'])

if __name__ == '__main__':
    app.run(debug=True)
