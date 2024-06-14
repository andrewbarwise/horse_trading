from flask import Flask, request, render_template
import pickle
import numpy as np
import pandas as pd
import os

from src.data_cleaning import DataCleaning

app = Flask(__name__)
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

@app.route('/')
def home():
    return render_template('index.html', races=[], race_data={})

@app.route('/predict', methods=['POST'])
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
    app.run(debug=True)
