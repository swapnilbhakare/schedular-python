from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, File, UploadFile,Form

from typing import Any, Optional

class ReportSchedule(BaseModel):
    start_date: str= Form(...)
    end_date: str
    time: str
    report_format: str
    ToEmailId: EmailStr
    email_subject: str
    email_body: str
    created_by: str
    username: str
    once_daily: int
    once_weekly: int
    once_monthly: int
    once: int
    once_every: int
    time_zone: str
    file: str= Form(...)
    reportType: str
    ModuleName: str