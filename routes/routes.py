from fastapi import APIRouter, UploadFile, HTTPException,Form,Request
from services.upload_on import upload_file_to_onedrive,get_access_token,upload_bytes_to_onedrive
from routes.schedular import insert_report_schedule,insert_data_report_schedule
from models.ReportSchedule import ReportSchedule
from fastapi import FastAPI, Form, File, UploadFile
from db_connection import connection
from typing import Optional
from pydantic import BaseModel
from services.exportService import dashboard_pdf
import io
router = APIRouter()

class User(BaseModel):
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/signup/")
async def sign_up(
   user: User
):

     try:
    #  Users
        
        cursor = connection.cursor()
        if user.password != user.confirm_password:
            print('wrong pass')
            return {"status": "failed", "message": "Password is not match",}

            # SQL INSERT statement
        insert_sql = """
                INSERT INTO [dbo].[Users]
                    (Email,Password,UserType)
                VALUES (?, ?,?)
            """
            # Values to be inserted
        values = (user.email,user.password,0)
     
            # Execute the query
        cursor.execute(insert_sql, values)
            # Commit the transaction
        connection.commit()

        return {"status": "success", "message": "Registration sucessfully...","userType":0}

     except:
       print('An exception occurred')
     


@router.post("/login/")
async def login(request: LoginRequest):
    try:
        cursor = connection.cursor()

        # Fetch user from the database
        cursor.execute("SELECT Password, UserType FROM [dbo].[Users] WHERE Email = ?", request.email)
        user_record = cursor.fetchone()

        if not user_record:
            return {"status": "failed", "message": "Invalid email or password"}

        stored_password, user_type = user_record

        # Check if password matches
        if request.password != stored_password:
            return {"status": "failed", "message": "Invalid email or password"}

        return {"status": "success", "message": "Login successful", "userType": user_type}

    except Exception as e:
        print(f"An exception occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")





@router.post("/insert-schedule/")
async def insert_schedule( 
    request: Request,
    start_date: str= Form(...),
    end_date:  str= Form(...),
    time: str= Form(...),
    report_format:  str= Form(...),
    ToEmailId: str= Form(...),
    email_subject:  str= Form(...),
    email_body: str= Form(...),
    created_by: str= Form(...),
    username: str= Form(...),
    once_daily: str= Form(...),
    once_weekly: str= Form(...),
    once_monthly: str= Form(...),
    once: str= Form(...),
    once_every: str= Form(...),
    time_zone: str= Form(...),
    # file: Optional[UploadFile] = File(None), 
    reportType: str= Form(...),
    moduleName: str= Form(...)):
    try:
            print('before pdf')
            # file= dashboard_pdf()
            pdf_file = await  dashboard_pdf(request)
            print('after pdf')

            access_token = get_access_token()
            file_name = "dashboard_report.pdf"
            if not access_token:
                raise HTTPException(status_code=500, detail="Access token could not be retrieved")
            download_url = None
            
            download_url = upload_bytes_to_onedrive(access_token, file_name, pdf_file)

            if not download_url:
                raise HTTPException(status_code=500, detail="Failed to upload file")
        
            # Call the actual function to insert the schedule
            file_link = download_url if download_url else None
            print(file_link,"file_link")
            result = insert_report_schedule(
                start_date,
                end_date,
                time,
                report_format,
                ToEmailId,
                email_subject,
                email_body,
                created_by,
                username,
                once_daily,
                once_weekly,
                once_monthly,
                once,
                once_every,
                time_zone,
                Link=download_url,
                reportType=reportType,
                ModuleName=moduleName,
            )
            return {"status": "success", "message": "Report schedule inserted successfully","result":result}
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))








@router.post("/insert-data-schedule/")
async def insert_data_schedule( 
    start_date: str = Form(...),
    end_date: str = Form(...),
    time: str = Form(...),
    username: str = Form(...),
    once_daily: str = Form(...),
    once_weekly: str = Form(...),
    once_monthly: str = Form(...),
    once: str = Form(...),
    once_every: str = Form(...),
    time_zone: str = Form(...),
    our_file: Optional[UploadFile] = File(None),
    compatitor_file: Optional[UploadFile] = File(None),
    reportType: str = Form(...),
    moduleName: str = Form(...),
    ):
    try:
            access_token = get_access_token()
            if not access_token:
                raise HTTPException(status_code=500, detail="Access token could not be retrieved")
            download_url_our_data = None
            download_url_compatitor_data= None
            

            try:
                download_url_our_data = upload_file_to_onedrive(access_token, our_file) if our_file else None
                download_url_compatitor_data = upload_file_to_onedrive(access_token, compatitor_file) if compatitor_file else None
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error uploading files: {str(e)}")
              
            

            result = insert_data_report_schedule(
            start_date=start_date,
            end_date=end_date,
            time=time,
            username=username,
            once_daily=once_daily,
            once_weekly=once_weekly,
            once_monthly=once_monthly,
            once=once,
            once_every=once_every,
            time_zone=time_zone,
            Link=download_url_our_data,
            competitor_data=download_url_compatitor_data,
            reportType=reportType,
            ModuleName=moduleName,
            )
            return {"status": "success", "message": "Report schedule inserted successfully","result":result}
    except Exception as e:
        print("hello guys i'm except")

        raise HTTPException(status_code=500, detail=str(e))