import pyodbc
import logging

connection = None
cnn_azure = (
    r"Driver={ODBC Driver 18 for SQL Server};"
    r"Server=tcp:writenback.database.windows.net,1433;"
    r"Database=DecisionAnalysisDatabase;"
    r"Uid=priyank;"
    r"Pwd=530228@mka;"
    r"Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
)
print(pyodbc.drivers())



def get_connection():
    global connection
    if connection is None or connection.closed:
        try:
            connection = pyodbc.connect(cnn_azure)
            logging.info("Connection to database established successfully.")
        except pyodbc.Error as e:
            logging.error("Database connection error: %s", e)
            raise
    return connection
