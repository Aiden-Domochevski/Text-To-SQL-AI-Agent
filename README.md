# Text-to-SQL Agent

An AI agent that answers business questions asked in plain English by querying a MySQL database. You write a question, the agent decides which SQL queries it needs, runs them, reads the results, and replies with a final answer.

Example question:

> What is our business about, what are our top selling products, and how much money did we make last month?

The agent explores the database on its own, finds the relevant tables, runs as many queries as it needs, and summarizes what it found.

## How it works

```
        user question
              |
              v
   +----------------------+        +---------------------------+
   |       main.py        | -----> |      Gemini (LLM)         |
   |  (loop + prompt)     | <----- |  decides what to query    |
   +----------------------+        +---------------------------+
        |            ^
  SQL   |            |  query results
  query |            |
        v            |
   +----------------------+
   |       tools.py       |
   |  runs the SQL query  |
   +----------------------+
              |
              v
   +----------------------+
   |   MySQL database     |
   |   (shop_analytics)   |
   +----------------------+
```

1. The question is sent to Gemini together with a description of the `query_database` tool.
2. Gemini replies with a request to run a SQL query.
3. `tools.py` executes the query on MySQL and returns the columns and rows.
4. The results are sent back to Gemini, which either asks for another query or decides it has enough information.
5. When the model sets `are_we_done` to true, the loop stops and the final answer is printed.

The model's replies follow a fixed JSON structure defined with Pydantic:

| Field | Purpose |
|-------|---------|
| `tables_list` | Tables the model considers relevant to the question |
| `query` | The SQL query the model wants to run |
| `result` | The final answer, filled in only at the end |
| `are_we_done` | Tells the loop when to stop |

## Project structure

```
.
├── main.py      # prompt, response schema and agent loop
├── tools.py     # MySQL connection and the query_database function
└── .env         # API keys (not committed)
```

## Requirements

- Python 3.10 or later
- A running MySQL server with a `shop_analytics` database
- A Gemini API key

Python packages:

```
google-genai
python-dotenv
pydantic
mysql-connector-python
requests
```

## Setup

Install the dependencies:

```bash
pip install google-genai python-dotenv pydantic mysql-connector-python requests
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_api_key
```

Set the MySQL connection details (host, port, user, password, database) in `tools.py`. The agent only reads data, so it is best to connect with a MySQL user that has `SELECT` permission only:

```sql
CREATE USER 'analyst_ro'@'%' IDENTIFIED BY 'your_password';
GRANT SELECT ON shop_analytics.* TO 'analyst_ro'@'%';
```

## Usage

The question is set in the `input` variable at the top of the main script in `main.py`. Change it to whatever you want to ask, then run:

```bash
python main.py
```

The script prints each tool call, the rows returned by the database, and finally the answer.