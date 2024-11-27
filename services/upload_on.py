from fastapi import FastAPI, UploadFile, HTTPException
from typing import Optional
import requests
from io import BytesIO
import logging
from config import Config
import httpx
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def get_access_token() -> Optional[str]:

    """Obtain an access token using client credentials."""

    try:

        url = f'{Config.AUTHORITY}/oauth2/v2.0/token'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        data = {

            'grant_type': 'password',

            'client_id': Config.CLIENT_ID,

            'client_secret': Config.CLIENT_SECRET,

            'username': Config.USERNAME,

            'password': Config.PASSWORD,

            'scope': ' '.join(Config.USER_SCOPES)

        }

        response = requests.post(url, headers=headers, data=data)

        response.raise_for_status()

        return response.json().get('access_token')

    except requests.RequestException as e:


        return None



def upload_file_to_onedrive(access_token: str, file: UploadFile) -> Optional[str]:
    """Upload the file to OneDrive and return the download URL."""
    try:
        file_name = file.filename
        url = f'https://graph.microsoft.com/v1.0/me/drive/root:/{file_name}:/content'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream'
        }
        response = requests.put(url, headers=headers, data=file.file)
        response.raise_for_status()
        return response.json().get('@microsoft.graph.downloadUrl')
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail="Failed to upload file to OneDrive")



# async def get_folder_data():
#     access_token =  get_access_token()  # Get the access token from your function
    
#     if not access_token:
#         print("Unable to obtain access token.")
#         return None
    
#     # Define the folder path and the SharePoint URL
#     folder_path = "/sites/decison-plus/Shared Documents/decison-ai-doc"
#     sharepoint_url = f"https://innovationalofficesolutio.sharepoint.com/_api/web/GetFolderByServerRelativeUrl('{Config.SHAREPOINT_DOC_LIB}')/Files"
    
#     # Set the headers for the GET request
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Accept": "application/json;odata=verbose",
#     }
    
#     # Make the GET request to fetch folder data
#     async with httpx.AsyncClient() as client:
#         response = await client.get(sharepoint_url, headers=headers)
#     # response = requests.get(sharepoint_url, headers=headers)
    
#     if response.status_code == 200:
#         # Parse the response
#         folder_data = response.json().get("d", {}).get("results", [])
        
#         if folder_data:
#             print(f"Successfully retrieved {len(folder_data)} file(s) from the folder.")
#             return folder_data
#         else:
#             print("No files found in the folder.")
#             return None
#     else:
#         print(f"Error fetching folder data: {response.status_code} {response.text}")
#         return None
