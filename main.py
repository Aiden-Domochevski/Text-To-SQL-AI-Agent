from google import genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tools import function_call, query_database

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class table(BaseModel):
    table_name : str = Field(description="this is the name of the table")

class database(BaseModel):
    result : str = Field(description="this should be empty until you the are_we_done is true so you can give the final answer the user based on the response of the system and the question of the input user answer the question that the user asked about using the context from the query responses of the previous iterations")
    are_we_done : bool = Field(description="this should be True when there is no need to proceed or check any other information so we can break the loop. otherwise it's False until you have the full context you need")

query_tool = {
    "type": "function",
    "name": "query_database",
    "description": "query anything you need from the database so you can respond to the user question and keep in mind we are using mysql database here so adjust your query to that and also we're using the shop_analytics database so no need to check for the databases and don't change or add anything to the database don't edit anything you are only capable of retrieving data do not change anything in the data, and you can do one query at a time per tool call, and also make sure that you have the necessary columns name etc before using arguments and other stuff if you don't know enough argument or columns get them and then query the database",
    "parameters": {
        "type": "object",
        "properties": { "query": {
                "type": "string",
                "description": "the query you need to answer the question or to investigate the system database and the tables",
            },},
    },
}

input="what is our business about and what are our top selling products and how much money did we make last month"
message=f"you are a data analyst/scientist. the user will input an english query about something you're job is to return the sql queries related the user input {input}"


interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=message,
        tools=[query_tool],
        response_format={
            "type":"text",
            "mime_type":"application/json",
            "schema":database.model_json_schema()
        }
    )
#results = database.model_validate_json(interaction.output_text)
arewedone = False

while not arewedone:
    for step in interaction.steps:
        if step.type == "function_call":
            print(f"Function call: {step.name} with args: {step.arguments}")
            results = function_call(step.name, step.arguments)
            print(results)
            message = f"role : tool, tool_id : {step.id} , name : {step.name}, results : {str(results)}"+"\n\n"+f"user_message or and context : {message}"
    interaction = client.interactions.create(
        model="gemini-3.1-flash-lite",
        input=message,
        tools=[query_tool],
        response_format={
            "type":"text",
            "mime_type":"application/json",
            "schema":database.model_json_schema()
        }
    )
    if interaction.output_text:
        arewedone = database.model_validate_json(interaction.output_text).are_we_done
    print(f"are we done : {arewedone}")

print(database.model_validate_json(interaction.output_text).result)
