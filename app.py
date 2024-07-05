from flask import Flask, request, render_template, redirect, url_for
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import numpy as np
import pandas as pd
import os
import secrets

from src.data_cleaning import DataCleaning

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Construct the absolute path for the model
model_path = os.path.join(os.path.dirname(__file__), 'models', 'base_model.pkl')

# Debugging statement to print the model path
print(f"Model path: {model_path}")

# Check if the model file exists
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found: {model_path}")

# Load the model
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# Ensure the loaded object is a model with predict method
if not hasattr(model, 'predict'):
    raise AttributeError(f"Loaded object is not a model with a predict method. Loaded object type: {type(model)}")

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Flask-Admin views
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('login'))
        return super(MyAdminIndexView, self).index()

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class UserAdmin(ModelView):
    column_list = ['username', 'is_admin']
    form_columns = ['username', 'password', 'is_admin']

    def on_model_change(self, form, model, is_created):
        if not model.password.startswith('pbkdf2:sha256'):
            model.password = generate_password_hash(model.password)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(UserAdmin(User, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('predict_page'))
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.index'))
            return redirect(url_for('predict_page'))
    return render_template('landing.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/predict_page')
@login_required
def predict_page():
    return render_template('index.html', races=[], race_data={}, selected_race=None)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        
        # Debugging statement to print the file path
        print(f"Uploaded file path: {filepath}")

        file.save(filepath)
        
        # Read the CSV file into a DataFrame
        data = pd.read_csv(filepath)

        # Debugging statement to print the data
        print(f"Data from CSV:\n{data.head()}")

        # Extract unique races
        races = data['Race Time'].unique().tolist()

        # Normalize columns using DataCleaning module
        data1 = DataCleaning.normalize_columns(data, ['SP Odds Decimal', 'weight', 
           'Proform Speed Rating', 'Won P/L Before', 'evening_morning_price'])
        
        # Create a dictionary to store DataFrame HTML for each race
        race_data = {}

        for race in races:
            race_df = data1[data1['Race Time'] == race].copy()
            
            # Drop columns not needed for prediction
            features = race_df[['SP Odds Decimal', 'weight', 
                    'Proform Speed Rating', 'Won P/L Before', 'evening_morning_price']].values
            
            # Make predictions
            predictions = model.predict(features)
            
            # Add predictions to the DataFrame
            race_df['Predictions'] = predictions
            race_data[race] = race_df.to_html(classes='data', header="true", index=False)
        
        # Ensure selected_race is valid
        selected_race = races[0] if races else None
        return render_template('index.html', races=races, race_data=race_data, selected_race=selected_race)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
