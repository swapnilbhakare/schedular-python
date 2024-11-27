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

app = FastAPI()
from routes.schedular import run_scheduler_forever
app.include_router(router)

from services.exportService import dashboard_pdf
templates = Jinja2Templates(directory="templates")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    # Load data from the JSON file
    with open('descriptive_dashboard_output.json') as f:
        data = json.load(f)
    
    pdf_content = dashboard_pdf(request)
    print(pdf_content)
    # Render the HTML template with data
    return templates.TemplateResponse("chart.html", {"request": request, "data": data})


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
