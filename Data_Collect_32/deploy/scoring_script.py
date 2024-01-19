# scoring_api.py

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import uvicorn
import json

app = FastAPI()

# Load the scikit-learn model
model_path = "model.pkl"
model = joblib.load(model_path)


class InputData(BaseModel):
    InputData: dict
    # Add other input fields as needed


@app.on_event("startup")
def save_openapi_json():
    openapi_data = app.openapi()
    # Change "openapi.json" to desired filename
    with open("openapi.json", "w") as file:
        json.dump(openapi_data, file)



@app.get("/")
def landing_page():
    return "Landing Page"


@app.post("/predict")
def predict(input_data: InputData):
    try:
        # Convert input data to a DataFrame
        new_data = pd.DataFrame.from_dict(input_data.dict(), orient="index").T

        # Convert Datum to datetime and other columns to numeric
        new_data["Datum"] = pd.to_datetime(new_data["Datum"], dayfirst=True)
        columns_to_convert = new_data.columns.difference(["Datum"])

        def convert_to_numeric(column):
            return pd.to_numeric(column, errors="coerce")

        new_data[columns_to_convert] = new_data[columns_to_convert].apply(
            convert_to_numeric
        )

        # Make predictions
        predictions = model.predict_proba(new_data) 

        # Convert predictions to a list
        predictions_list = str(float(predictions[:, 1]))

        return predictions_list

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":


    uvicorn.run(app)
