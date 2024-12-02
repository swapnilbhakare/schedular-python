from fastapi import FastAPI,Request
from routes.routes import router
import threading
from fastapi import FastAPI
import pyodbc
import json
from db_connection import get_connection
from datetime import datetime
from dateutil import tz, parser 
from services.email_service import send_email
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,FileResponse
# from weasyprint import HTML
from fastapi.staticfiles import StaticFiles

app = FastAPI()
from routes.schedular import run_scheduler_forever
app.include_router(router)

from services.exportService import dashboard_pdf
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/dashboard", response_class=HTMLResponse)

async def dashboard(request: Request):
    # List of JSON files to load
    json_files = [
        "anomaly_detection.json",
        "descriptive_dashboard_output.json",
        "diagnostic_analysis.json",
        "predictive_dashboard_output.json",
        "prescriptive_analysis.json"
    ]

    # Create an empty dictionary to store combined data under specific keys
    combined_data = {}

    # Load data from each JSON file and store it under its filename key
    for file in json_files:
        try:
            with open(file) as f:
                file_data = json.load(f)
                # Store the data and filename under the key
                key_name = file.replace(".json", "")  # e.g., "anomaly_detection"
                combined_data[key_name] =file_data
                print(f"Data from {file} added under '{key_name}' key.")
        except FileNotFoundError:
            print(f"Warning: {file} not found, skipping.")
        except json.JSONDecodeError as e:
            print(f"Error decoding {file}: {e}, skipping.")

    # Render the HTML template with the combined data
    return templates.TemplateResponse("chart.html", {"request": request, "data": combined_data})

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':

    scheduler_thread = threading.Thread(target=run_scheduler_forever)
    scheduler_thread.start()
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)
else:
    scheduler_thread = threading.Thread(target=run_scheduler_forever)
    scheduler_thread.start()
