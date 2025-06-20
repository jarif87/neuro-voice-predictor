from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pickle
import numpy as np
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load the pre-trained model
with open("catboost_model.pkl", "rb") as file:
    model = pickle.load(file)

# Pydantic model for input validation
class ParkinsonsInput(BaseModel):
    spread1: float
    PPE: float
    spread2: float
    MDVP_Fo_Hz: float
    MDVP_Flo_Hz: float

# Home route to serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "prediction": None}
    )

# Prediction endpoint
@app.post("/predict", response_class=HTMLResponse)
async def predict(
    request: Request,
    spread1: float = Form(...),
    PPE: float = Form(...),
    spread2: float = Form(...),
    MDVP_Fo_Hz: float = Form(...),
    MDVP_Flo_Hz: float = Form(...)
):
    # Prepare input data in the correct order
    input_data = np.array([[spread1, PPE, spread2, MDVP_Fo_Hz, MDVP_Flo_Hz]])
    prediction = model.predict(input_data)[0]
    prediction_text = "Parkinson’s Disease Detected" if prediction == 1 else "No Parkinson’s Disease Detected"
    
    # Return the template with prediction and input values
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "prediction": prediction_text,
            "input_data": {
                "spread1": spread1,
                "PPE": PPE,
                "spread2": spread2,
                "MDVP:Fo(Hz)": MDVP_Fo_Hz,
                "MDVP:Flo(Hz)": MDVP_Flo_Hz
            }
        }
    )