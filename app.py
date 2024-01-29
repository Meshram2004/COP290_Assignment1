from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from jugaad_data.nse import stock_csv, stock_df
from datetime import datetime, timedelta,date,time
import pandas as pd

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

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/stock_analysis', methods=['GET', 'POST'])
def stock_analysis():
    # Dummy data for dropdown options
    #start_dates = []
    #end_dates = []
    stocks = ['select','ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJFINSV', 'BAJFINANCE', 'BANKBARODA', 'BERGEPAINT', 
    'BHARTIARTL', 'BPCL', 'CANBK', 'CIPLA', 'COALINDIA', 'CUMMINSIND', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'FEDERALBNK', 'GRASIM', 'HCLTECH', 
    'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDPETRO', 'HINDUNILVR', 'ICICIBANK', 'INDUSINDBK', 'INFY', 'IOC', 'ITC', 'JSWSTEEL', 'KOTAKBANK', 
    'LTIM', 'LT', 'MARUTI', 'NESTLEIND', 'NTPC', 'ONGC', 'PFC', 'PNB', 'SBILIFE', 'SBIN', 'SHREECEM', 'TATACONSUM', 'TATASTEEL', 'TECHM', 'TVSMOTOR', 
    'ULTRACEMCO', 'UPL', 'ZYDUSLIFE']
    analysis_types = ['select', 'Market Price','Value','LTP']
    time_scale = ['select','1 Day','1 Week','1 Month','1 Year','3 Years','5 Years']
    if request.method == 'POST':
        # Handle form submission if needed
        #selected_start_date = request.form.get('start_date')
        #selected_end_date = request.form.get('end_date')
        selected_stock = request.form.get('stock')
        selected_analysis_type = request.form.get('analysis_type')
        selected_time_scale = request.form.get('time')
        # Perform analysis or redirect as needed

        if selected_time_scale== '1 Day':
            x=1
        elif selected_time_scale== '1 Week':
            x=7
        elif selected_time_scale== '1 Month':
            x=30
        elif selected_time_scale== '1 Year':
            x=365
        elif selected_time_scale== '3 Years':
            x=1095
        elif selected_time_scale== '5 Years':
            x=1825
        if selected_stock != 'select' and selected_analysis_type != 'select' and selected_time_scale != 'select':
            end_date = date.today()
            start_date = end_date - timedelta(x)  

            Details = stock_df(selected_stock, start_date, end_date)
            
            required_columns = ['DATE', 'CLOSE', 'LTP','VALUE']
            Details_required = Details[required_columns]
            Details_required['DATE'] = pd.to_datetime(Details_required['DATE'])

            #sorting the dates so that start_date is in the beginning and end_date is in the end
            Details_required = Details_required.sort_values(by='DATE')

            # first we are saving the csv files and then os will read the csv files to plot the graph
            csv_path = f"{selected_stock}.csv"
            Details_required.to_csv(csv_path, index=False)
        
    
            #index tells how the data will be written, when it is false S.no. do not appear but when it is 
            #true an additional column of kind-of-serial-nums is created 
            Details_required.to_csv(csv_path, index=False)



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

if __name__ == '__main__':
    app.run(debug=True)