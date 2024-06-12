from flask import Flask, request, render_template
import pickle
import numpy as np
import pandas as pd
import os

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
    return render_template('index.html', prediction=None)

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

        # Assuming the DataFrame contains the necessary features
        features = data.values
        
        # Debugging statement to print the features
        print(f"Features for prediction:\n{features}")

        # Make predictions
        predictions = model.predict(features)
        
        # Convert predictions to a list to render in HTML
        predictions = predictions.tolist()
        return render_template('index.html', prediction=predictions)

if __name__ == '__main__':
    app.run(debug=True)
