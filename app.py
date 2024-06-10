from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model_path = os.path.join(os.path.dirname(__file__), 'models', 'base_model.pkl')


# load the model
with open(model_path, 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']

    if file.filename == '':
        return 'No selected file'
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # read the csv file in a pandas df
        data = pd.read_csv(filepath)
        features = data.values

        # make predictions
        predictions = model.predict(features)

        # convert the predictions to a list to render in HTML
        predictions = predictions.tolist()

        return render_template('index.html', prediction = predictions)
    
if __name__ == '__main__':
    app.run(debug=True)
    