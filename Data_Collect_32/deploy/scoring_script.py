# scoring_api.py

import joblib
import json
from flask import Flask, request, jsonify
import pandas as pd
from sklearn.preprocessing import StandardScaler  # If scaling is part of your model preprocessing

app = Flask(__name__)

# Load the scikit-learn model
model_path = 'deploy/model.pkl'
model = joblib.load(model_path)


@app.route('/')
def landing_page():
    return 'Landing Page'
# Define a route for scoring
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse input data from JSON
        input_data = request.get_json()

        # Convert JSON data to a DataFrame
        new_data = pd.DataFrame.from_dict(input_data, orient = "index").T

        # Perform preprocessing on the new data
        scaler = StandardScaler()
        preprocessed_data = scaler.fit_transform(new_data)

        # Make predictions
        predictions = model.predict(preprocessed_data)

        # Convert predictions to a list
        predictions_list = predictions.tolist()

        return jsonify({'predictions': predictions_list})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
