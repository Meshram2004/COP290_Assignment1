from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import yfinance as yf

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Initialize Database within Application Context
with app.app_context():
    db.create_all()

def get_stock_value(stock_symbol, filter_type):
    try:
        stock_data = yf.Ticker(stock_symbol + ".NS")
        if filter_type == 'filter1':
            filtered_data = stock_data.info.get('trailingPE')
            print("hifilter 1")
        elif filter_type == 'filter2':
            print("hifilter 2 before")
            filtered_data = stock_data.info.get('returnOnAssets')
            print("hifilter 2 after")
        else:
            filtered_data = stock_data.info.get('netIncome')
        
        if filtered_data is not None:
            return filtered_data
        else:
            return None
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('welcome.html', username=session['username'])
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/Filters', methods=['GET', 'POST'])
def Filters():
    if request.method == 'POST':
        filters = request.form.getlist('filter')
        stocks = request.form.getlist('stock')
        values = request.form.getlist('dynamicInput')
        print(filters)
        print(stocks)
        print(values)
        filtered_stocks = []

        for stock_symbol in stocks:
            stock_values = []
            print("hi103")

            for filter_type, filter_value in zip(filters, values):
                filter_value = float(filter_value)
                stock_value = get_stock_value(stock_symbol, filter_type)
                print(stock_value)

                if stock_value is not None and stock_value > filter_value:
                    stock_values.append({"filter_type": filter_type, "value": stock_value})
                    print(stock_values)

                print("hi108")
            if stock_values:
                filtered_stocks.append({"symbol": stock_symbol, "values": stock_values})
                print(filtered_stocks)

        return render_template('Filters.html', filtered_stocks=filtered_stocks)

    return render_template('Filters.html')

if __name__ == '__main__':
    app.run(debug=True)
