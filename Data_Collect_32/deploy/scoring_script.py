# scoring_api.py

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import uvicorn
import json
import os

from swagger_for_mkdocs.transform_swagger_json import save_openapi_config


app = FastAPI()

class InputData(BaseModel):
    InputData: dict = {'test': 'test1'}


def get_model(model_name: str = "model.pkl") -> any:
    # Get the current directory of the script
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # Construct the relative path to the model file
    model_path = os.path.join(current_directory, model_name)
    
    # Check if the model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_name}' not found in the current directory.")
    
    # Load the model
    model = joblib.load(model_path)
    return model


@app.get("/")
def landing_page():
    return {'message:': "Landing Page"}


@app.post("/predict")
def predict(input_data):
    try:
        # Convert input data to a DataFrame
        new_data = pd.DataFrame.from_dict(input_data.model_dump(), orient="index").T

        # Convert Datum to datetime and other columns to numeric
        new_data["Datum"] = pd.to_datetime(new_data["Datum"], dayfirst=True)
        columns_to_convert = new_data.columns.difference(["Datum"])

        def convert_to_numeric(column):
            return pd.to_numeric(column, errors="coerce")

        new_data[columns_to_convert] = new_data[columns_to_convert].apply(
            convert_to_numeric
        )

        # Make predictions
        predictions = MODEL.predict_proba(new_data) 

        # Convert predictions to a list
        predictions_list = str(float(predictions[:, 1]))

        return predictions_list

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":

    MODEL = get_model
    uvicorn.run(app, host = "127.0.0.1", port = 500)


save_openapi_config(app, 'docs/', host='http://127.0.0.1:500', title = 'Forex Trading')
 