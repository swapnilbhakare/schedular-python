
import threading
from fastapi import FastAPI


app = FastAPI()



import schedule
import time


import pyodbc
import json
from db_connection import get_connection
from datetime import datetime
from dateutil import tz, parser 
from services.email_service import send_email
from fastapi.responses import JSONResponse

connection = get_connection()

if connection:
    print("Connection successful!")




def insert_data_report_schedule(start_date,
                end_date,
                time,
                username,
                once_daily,
                once_weekly,
                once_monthly,
                once,
                once_every,
                time_zone,
                Link,
                competitor_data,
                reportType,
                ModuleName,
                ):
    try:

        if connection is None:
            return

        cursor = connection.cursor()

        # SQL INSERT statement
        insert_sql = """
            INSERT INTO [dbo].[DataRefreshSchedules]
    ( [start_date], [end_date], [time], [username], [once_daily], [once_weekly], 
     [once_monthly], [once], [once_every], [time_zone], [Link], [reportType], [ModuleName],[competitor_data])
VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)

        """

        # Values to be inserted
        values = ( start_date, end_date, time, username, once_daily, once_weekly, 
          once_monthly, once, once_every, time_zone, Link, reportType, ModuleName,competitor_data)
        print(insert_sql,values)
        # Execute the query
        cursor.execute(insert_sql, values)
        run_scheduler_for_data_record()
        
        # Commit the transaction
        connection.commit()
    
    except Exception as err:
        print(f"An exception occurred: {err}")
    
    finally:
        if cursor:
            cursor.close()
        # if connection:
        #     print("Closing connection...")
        #     connection.close()


def insert_report_schedule(start_date, end_date, time, report_format, ToEmailId, email_subject,
                           email_body, created_by, username, once_daily, once_weekly, once_monthly,
                           once, once_every, time_zone, Link, reportType, ModuleName):
    try:

        if connection is None:
            return

        cursor = connection.cursor()

        # SQL INSERT statement
        insert_sql = """
            INSERT INTO [dbo].[ReportSchedules]
                ([start_date], [end_date], [time], [report_format], [ToEmailId], [email_subject], 
                 [email_body], [created_by], [username], [once_daily], [once_weekly], [once_monthly], 
                 [once], [once_every], [time_zone], [Link], [reportType], [ModuleName])
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Values to be inserted
        values = (start_date, end_date, time, report_format, ToEmailId, email_subject, email_body,
                  created_by, username, once_daily, once_weekly, once_monthly, once, once_every,
                  time_zone, Link, reportType, ModuleName)

        # Execute the query
        cursor.execute(insert_sql, values)
        run_scheduler_for_new_record()
        
        # Commit the transaction
        connection.commit()
    
    except Exception as err:
        print(f"An exception occurred: {err}")
    
    finally:
        if cursor:
            cursor.close()
        # if connection:
        #     print("Closing connection...")
        #     connection.close()


def format_time_for_schedule(time_str):
    time_obj = datetime.strptime(str(time_str), "%H:%M:%S")
    formatted_time = time_obj.strftime("%H:%M:%S")
    return formatted_time

def scheduledJobs(report_info):
    end_date = report_info['end_date']
    date_format = "%Y-%m-%d"
    current_time_utc = datetime.now(tz.tzutc())
    end_date_obj = datetime.strptime(str(end_date), date_format)
    formatted_time = format_time_for_schedule(report_info['time'])
    given_time_utc = parser.parse(formatted_time).replace(tzinfo=tz.tzutc())
    local_timezone = tz.tzlocal()
    localized_time = given_time_utc.astimezone(local_timezone)
    time_obj = datetime.fromisoformat(str(localized_time))
    formatted_time = time_obj.time().strftime("%H:%M:%S")
    scheduled_datetime = datetime.combine(end_date_obj.date(), given_time_utc.time(), tzinfo=tz.tzutc())
    
    
    if scheduled_datetime > current_time_utc:
        if report_info['once']:
            schedule.every().day.at(formatted_time).do(job_that_executes_once, report_info).tag(report_info['id'], 'once')
        elif report_info['once_daily']:
            schedule.every().day.at(formatted_time).until(end_date_obj).do(send_report_email, report_info).tag(report_info['id'], 'once_daily')
        elif report_info['once_weekly']:
            schedule.every().monday.until(end_date_obj).at(formatted_time).do(send_report_email, report_info).tag(report_info['id'], 'once-weekly')
        elif report_info['once_monthly']:
            schedule.every(31).day.until(end_date_obj).at(formatted_time).do(send_report_email, report_info).tag(report_info['id'], 'once-monthly')
        elif report_info.get('once_every'):
            schedule.every(report_info['once_every']).days.until(end_date_obj).at(formatted_time).do(send_report_email, report_info).tag(report_info['id'], 'once-every')



def scheduledDataJobs(report_info):
    end_date = report_info['end_date']
    date_format = "%Y-%m-%d"
    current_time_utc = datetime.now(tz.tzutc())
    end_date_obj = datetime.strptime(str(end_date), date_format)
    formatted_time = format_time_for_schedule(report_info['time'])
    given_time_utc = parser.parse(formatted_time).replace(tzinfo=tz.tzutc())
    local_timezone = tz.tzlocal()
    localized_time = given_time_utc.astimezone(local_timezone)
    time_obj = datetime.fromisoformat(str(localized_time))
    formatted_time = time_obj.time().strftime("%H:%M:%S")
    scheduled_datetime = datetime.combine(end_date_obj.date(), given_time_utc.time(), tzinfo=tz.tzutc())
    Link=report_info['Link']
    reportType= report_info['reportType']
    
    if scheduled_datetime > current_time_utc:
        if report_info['once']:
            schedule.every().day.at(formatted_time).do(job_that_executes_once, report_info).tag(report_info['id'], 'once')
        elif report_info['once_daily']:
            schedule.every().day.at(formatted_time).until(end_date_obj).do(send_report_email, report_info).tag(report_info['id'], 'once_daily')
        elif report_info['once_weekly']:
            schedule.every().monday.until(end_date_obj).at(formatted_time).do(send_report_email, report_info).tag(report_info['id'], 'once-weekly')
        elif report_info['once_monthly']:
            schedule.every(31).day.until(end_date_obj).at(formatted_time).do(send_report_email, report_info).tag(report_info['id'], 'once-monthly')
        elif report_info.get('once_every'):
            schedule.every(report_info['once_every']).days.until(end_date_obj).at(formatted_time).do(send_report_email, report_info).tag(report_info['id'], 'once-every')


def job_that_executes_once(report_info):
    # add your function Link,reportType
    
    send_report_email(report_info)
    return schedule.CancelJob



def send_report_email(report_info):
    result = []

    try:
        # Extract and process email addresses
        if isinstance(report_info['ToEmailId'], str):
            email_list = [email.strip() for email in report_info['ToEmailId'].split(',')]
        else:
            raise ValueError("ToEmailId must be a string of email addresses separated by commas.")


        for email in email_list:
            DEFAULT_SUBJECT = 'Urgent Notification'
            DEFAULT_BODY = "Please take a look at the attachment"

            # Fetch subject and body from report_info or use defaults
            email_subject = report_info.get('email_subject', DEFAULT_SUBJECT)
            email_body = report_info.get('email_body', DEFAULT_BODY)

            # Fallback to default if subject or body is empty
            if not email_subject.strip():
                email_subject = DEFAULT_SUBJECT
            if not email_body.strip():
                email_body = DEFAULT_BODY

            try:
                download_link = report_info.get('Link', None)  
                if download_link:
                    download_button_html = f'<a href="{download_link}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; font-size: 16px;" target="_blank">Download Report</a>'
                else:
                    download_button_html = "<p>No download link provided.</p>"
                
                html_content = f"""
                <html>
                    <body>
                        <p>{email_body}</p>
                        {download_button_html}
                    </body>
                </html>
                """

                attachment = None  
                response = send_email(to_email=email, subject=email_subject, html_content=html_content, attachment=attachment)


                result.append({
                    "Receiver": email,
                    "status": response.get('status', 'Failed'),
                    "message_id": response.get('message_id', None),
                    "error": response.get('error', None)
                })
            except Exception as e:
                result.append({"Receiver": email, "status": 'Failed', "error": str(e)})

    except Exception as e:
        result = [{"status": 'Failed', "error": str(e)}]

    return JSONResponse(content=result)


def run_scheduler_for_data_record():
    try:
        conn = connection
        cursor = conn.cursor()
        cursor.execute('SELECT TOP 1 * FROM DataRefreshSchedules ORDER BY ID DESC')
        column_names = [column[0] for column in cursor.description]
        latest_schedules = dict(zip(column_names, cursor.fetchone()))
        if latest_schedules:
            scheduledDataJobs(latest_schedules)
    except Exception as e:
        print(f"Exception in run_scheduler_for_data_record: {e}")
    finally:
        if cursor:
            cursor.close()


def run_scheduler_for_new_record():
    try:
        conn = connection
        cursor = conn.cursor()
        cursor.execute('SELECT TOP 1 * FROM ReportSchedules ORDER BY ID DESC')
        column_names = [column[0] for column in cursor.description]
        latest_schedules = dict(zip(column_names, cursor.fetchone()))
        if latest_schedules:
            scheduledJobs(latest_schedules)
    except Exception as e:
        print(f"Exception in run_scheduler_for_new_record: {e}")
    finally:
        if cursor:
            cursor.close()
        

def run_scheduler_forever():
 
    while True:
        schedule.run_pending()  
