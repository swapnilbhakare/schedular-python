from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
# from weasyprint import HTML
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from xhtml2pdf import pisa
import json
import io
templates = Jinja2Templates(directory="templates")

from jinja2 import Template
from xhtml2pdf import pisa
import json
import io

def dashboard_pdf(request: Request):
    # Load data from the JSON file
    with open('descriptive_dashboard_output.json') as f:
        data = json.load(f)

    # Render the HTML template using Jinja2 directly
    with open("templates/chart.html", "r") as file:
        template = Template(file.read())
    
    rendered_html = template.render(request=request, data=data)

    # Convert the rendered HTML to a PDF
    pdf_file = io.BytesIO()  # Create an in-memory buffer
    pisa_status = pisa.CreatePDF(rendered_html, dest=pdf_file)

    if pisa_status.err:
        return {"error": "PDF generation failed"}

    # Move to the beginning of the BytesIO object
    pdf_file.seek(0)

    # Return the generated PDF file bytes
    return pdf_file.getvalue()
