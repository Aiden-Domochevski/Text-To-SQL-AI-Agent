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

def search_news():
    url = "https://api.nytimes.com/svc/topstories/v2/us.json"
    r = requests.get(url, params={"api-key": os.environ.get("NYTIMES_API_KEY")})
    r.raise_for_status()
    data = r.json()
    news_titles=[]
    for article in data["results"]:
        news_titles.append(f"{article['title']} -> {article['url']}")
    return news_titles



def query_database(query):
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description] if cursor.description else []
    return {"columns": columns, "rows": rows}

def function_call(name, args):
    if name == "query_database":
        return query_database(**args)

