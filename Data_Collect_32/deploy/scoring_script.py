# scoring_api.py

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import uvicorn
import json

app = FastAPI()

# Load the scikit-learn model
model_path = "model.pkl"
model = joblib.load(model_path)



# Define CORS settings
origins = ["*"]  # Allow requests from any origin

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    InputData: dict
    # Add other input fields as needed


# def save_openapi_json():
#     app.title = "Forex Trading Bot"
#     app.openapi_tags = None
#     app.version = ''
    
#     # for i, _ in enumerate(app.routes): 
#     #     app.routes[i].path = 'http://127.0.0.1:500' + app.routes[i].path
#     openapi_data = app.openapi()
#     openapi_data['host'] = 'http://127.0.0.1:500'
#     openapi_data['dom_id'] = 'http://127.0.0.1:500'
#     openapi_data['url'] = 'http://127.0.0.1:500'
#     # Change "openapi.json" to desired filename
#     with open("docs/openapi.json", "w") as file:
#         json.dump(openapi_data, file)





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
        predictions = model.predict_proba(new_data) 

        # Convert predictions to a list
        predictions_list = str(float(predictions[:, 1]))

        return predictions_list

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":


    uvicorn.run(app, host = "localhost", port = 500)

# save_openapi_json()
 
