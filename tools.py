import requests
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

conn = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    database=os.environ["DB_NAME"],
)

cursor = conn.cursor()



def query_database(query):
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        return {"columns": columns, "rows": rows}
    except Exception as e:
        return {"columns": [], "rows": [], "error": str(e)}


def function_call(name, args):
    if name == "query_database":
        return query_database(**args)

