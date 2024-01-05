# scoring_api.py

import joblib
from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the scikit-learn model
model_path = "deploy/model.pkl"
model = joblib.load(model_path)


@app.route("/")
def landing_page():
    return "Landing Page"


# Define a route for scoring
@app.route("/predict", methods=["POST"])
def predict():
    input_data = request.get_json()
    app.logger.info(input_data)
    new_data = pd.DataFrame.from_dict(input_data, orient="index").T
    app.logger.info(new_data.columns)
    # Convert JSON data to a DataFrame
    columns_to_convert = new_data.columns.difference(["Datum"])

    def convert_to_numeric(column):
        return pd.to_numeric(column, errors="coerce")

    new_data["Datum"] = pd.to_datetime(new_data["Datum"], dayfirst=True)
    new_data[columns_to_convert] = new_data[columns_to_convert].apply(
        convert_to_numeric
    )
    try:
        # Parse input data from JSON

        # Make predictions
        predictions = model.predict_proba(new_data)

        # Convert predictions to a list
        predictions_list = str(float(predictions.T[1]))

        return predictions_list

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=5050, debug=True)
