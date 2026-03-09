from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from research_and_analyst.database.db_config import SessionLocal, User, hash_password, verify_password
from research_and_analyst.api.services.report_service import ReportService