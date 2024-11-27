class Config:
    # BASE_URL="https://magic-grid-api-app.azurewebsites.net"
    BASE_URL="http://localhost:8000"
    SENDGRID_API_KEY='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'
    CLIENT_ID = "46006a21-36a1-44cd-a75a-1965799fcdd8"
    CLIENT_SECRET = "81c8Q~2_bxTXti9e~Pi9NiP3E-1G_Xz22pJHhaOL"
    TENANT_ID = "99fa199d-2653-4e16-bd65-17cc244b425e"
    USERNAME = "priyank@innovationalofficesolution.com"
    PASSWORD = "MagicGrid@9876"
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    USER_SCOPES = [
        'Chat.ReadWrite',
        'User.Read',
        'Files.ReadWrite',
        'Sites.ReadWrite.All'
    ]
    SHAREPOINT_SITE_URL = "https://innovationalofficesolutio.sharepoint.com/sites/decisionplus"
    SHAREPOINT_DOC_LIB = "/sites/decisionplus/Shared Documents"
    SCOPE = ["User.Read", "User.ReadBasic.All", "User.Read.All"]
    FROM_EMAIL=  "admin@innovationalofficesolution.com"
    FROM_AZURE_EMAIL="DoNotReply@innovationalofficesolution.com"
    CLIENT_SCOPES = ['https://graph.microsoft.com/.default']
    COMMUNICATION_SERVICE_CONNECTION_STRING = "endpoint=https://magic-grid-email-service-by-communication-service.unitedstates.communication.azure.com/;accesskey=7dFjgMiIhTwGnzY0cnq4e74giXLwHDZLwd01dIn2lwvbatCg8jezJQQJ99AKACULyCpYQd7xAAAAAZCS06Rq"