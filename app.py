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
        # Get historical data for the stock
        stock_data = yf.download(stock_symbol, start='2024-01-01', end='2024-01-20')
        
        # Perform filtering based on filter_type
        if filter_type == 'filter1':
            # Your filtering logic for filter1 (e.g., use close prices)
            filtered_data = stock_data['Close']
        elif filter_type == 'filter2':
            # Your filtering logic for filter2
            # Replace this with your actual filtering logic based on the filter_type
            filtered_data = stock_data['Open']
        else:
            # Default to close prices if filter_type is unknown
            filtered_data = stock_data['Close']
        
        # Check if filtered_data is not empty
        if not filtered_data.empty:
            # Return the last value in the filtered data
            last_value = filtered_data.iloc[-1]
            return last_value
        else:
            # Handle the case when filtered_data is empty
            return None
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {str(e)}")
        # Return a default value or handle the error appropriately
        return None


@app.route('/filter_stocks', methods=['POST'])
def filter_stocks():
    data = request.get_json()
    print("hi")
    filtered_stocks = []
    print(data['stocks'])
    for stock_symbol in data['stocks']:
        stock_value = get_stock_value(stock_symbol, data['filters'][0])  # Assuming only one filter for simplicity
        if stock_value > data['values'][0]:
            filtered_stocks.append({"symbol": stock_symbol, "value": stock_value})

    return jsonify(filtered_stocks)


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

@app.route('/Filters')
def Filters():
    return render_template('Filters.html')

if __name__ == '__main__':
    app.run(debug=True)
