class Config:
    # BASE_URL="https://magic-grid-api-app.azurewebsites.net"
    BASE_URL="http://localhost:8000"
    CLIENT_ID = ""
    CLIENT_SECRET = ""
    TENANT_ID = ""
    USERNAME = ""
    PASSWORD = ""
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    USER_SCOPES = [
        'Chat.ReadWrite',
        'User.Read',
        'Files.ReadWrite',
        'Sites.ReadWrite.All'
    ]
    SHAREPOINT_SITE_URL = ""
    SHAREPOINT_DOC_LIB = ""
    SCOPE = ["User.Read", "User.ReadBasic.All", "User.Read.All"]
    FROM_EMAIL=  ""
    FROM_AZURE_EMAIL=""
    CLIENT_SCOPES = ['https://graph.microsoft.com/.default']
    COMMUNICATION_SERVICE_CONNECTION_STRING = ""