# import schedule
# import pytz
import threading
from fastapi import FastAPI
# from datetime import datetime
# import asyncio

app = FastAPI()



import schedule
import time

# def job():
#     print("I'm working...")

# # schedule.every(10).seconds.do(job)
# # schedule.every().hour.do(job)
# # schedule.every().day.at("10:30").do(job)
# # schedule.every().monday.do(job)
# # schedule.every().wednesday.at("13:15").do(job)
# schedule.every().day.at("06:25").do(job)
# schedule.every().minute.at(":17").do(job)

# while True:
#     schedule.run_pending()
#     time.sleep(1)

import pyodbc
import json
from db_connection import get_connection
from datetime import datetime
from dateutil import tz, parser 
from services.email_service import send_email
from fastapi.responses import JSONResponse

# Assuming get_connection() provides the connection object
connection = get_connection()

if connection:
    print("Connection successful!")




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
            print("Closing cursor...")
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


def job_that_executes_once(report_info):
    send_report_email(report_info)
    return schedule.CancelJob



def send_report_email(report_info):
    print(f"Sending email for report_info: {report_info}")
    result = []

    try:
        # Extract and process email addresses
        if isinstance(report_info['ToEmailId'], str):
            email_list = [email.strip() for email in report_info['ToEmailId'].split(',')]
        else:
            raise ValueError("ToEmailId must be a string of email addresses separated by commas.")

        print(f"Parsed email list: {email_list}")

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

            print(email, "Processing email...")
            try:
                html_content = f"<html><body><p>{email_body}</p></body></html>"
                attachment = None  # Replace with actual attachment logic if required

                # Send the email using your email service
                response = send_email(to_email=email, subject=email_subject, html_content=html_content, attachment=attachment)

                print(f"Email sent to {email}: {response}")

                result.append({
                    "Receiver": email,
                    "status": response.get('status', 'Failed'),
                    "message_id": response.get('message_id', None),
                    "error": response.get('error', None)
                })
            except Exception as e:
                print(f"Error sending email to {email}: {e}")
                result.append({"Receiver": email, "status": 'Failed', "error": str(e)})

    except Exception as e:
        print(f"Error processing report_info: {e}")
        result = [{"status": 'Failed', "error": str(e)}]

    print('Email process completed.')
    return JSONResponse(content=result)

def run_scheduler_for_new_record():
    print("Running scheduler for new record...")
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
        # traceback.print_exc()
    finally:
        if cursor:
            print("Closing cursor...")
            cursor.close()
        # if conn:
        #     print("Closing connection...")
        #     conn.close()

def run_scheduler_forever():
    start_date = '2024-11-16'
    end_date = '2024-11-16'
    time = '09:52:00'
    report_format = 'PDF'
    ToEmailId = 'swapnil@innovationalofficesolution.com'
    email_subject = 'Scheduled Report'
    email_body = 'Please find the attached report.'
    created_by = 'allu'
    username = 'allu'
    once_daily = 1
    once_weekly = 0
    once_monthly = 0
    once = 1
    once_every = 1
    time_zone = 'UTC'
    Link = 'http://example.com/report'
    reportType = 'Summary'
    ModuleName = 'Finance'

    # Insert report schedule
    insert_report_schedule(start_date, end_date, time, report_format, ToEmailId, email_subject, email_body,
                           created_by, username, once_daily, once_weekly, once_monthly, once, once_every,
                           time_zone, Link, reportType, ModuleName)
    while True:
        schedule.run_pending()  # Check for pending scheduled jobs
        # time.sleep(1)  # Wait for 1 second before checking again


