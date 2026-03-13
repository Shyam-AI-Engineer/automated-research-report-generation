from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
from research_and_analyst.api.routes import report_routes
from datetime import datetime

app = FastAPI(title="Autonomous Report Generator UI")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="research_and_analyst/api/templates")
app.templates = templates  # so templates accessible inside router