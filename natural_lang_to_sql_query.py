import os
import re
import json
import psycopg2
from langchain.chains import LLMChain

from langchain_core.prompts import PromptTemplate

from langchain.chains import LLMChain

# --- CONFIGURATION ---
DB_CONFIG = {
    "dbname": "db_name",
    "user": "",
    "password": "",
    "host": "",
    "port": 5432,
}

# Path to downloaded local GGUF model (e.g., Mistral or SQLCoder)
LLM_PATH = "/path/to//sqlcoder-7b.Q4_K_M.gguf"  # Change as needed


from langchain_community.llms import LlamaCpp

llm = LlamaCpp(
    model_path=LLM_PATH,
    temperature=0.2,
    max_tokens=512,
    top_p=0.95,
    n_ctx=10048,
    n_gpu_layers=10,
    n_threads=4,  # ← replace with your actual physical core count
    verbose=True  # Optional: shows inference output,
)

import psycopg2


def get_db_schema(tables: list[str] = None):
    if tables:
        where_clause = f"AND table_name IN ({','.join(['%s'] * len(tables))})"
    else:
        where_clause = ""

    conn = psycopg2.connect(
        dbname="db_name",
        user="",
        password="",
        host="",
        port=5432
    )
    cur = conn.cursor()

    schema = []
    cur.execute(f"""
        SELECT table_name, column_name
        FROM information_schema.columns
        WHERE table_schema = 'public' {where_clause}
        ORDER BY table_name, ordinal_position;
    """, tables if tables else [])
    for table, column in cur.fetchall():
        schema.append(f"{table}.{column}")

    cur.close()
    conn.close()

    return "\n".join(schema)

schema_text = get_db_schema(['users', 'visit', 'conveyance'])

# Prompt to convert user query → SQL using the database schema
prompt = PromptTemplate(
    input_variables=["user_query"],
    template="""
You are a safe SQL assistant. Only use the tables and columns mentioned below.
Schema:
{schema_text}.Only generate SQL SELECT queries based on the user's intent.
NEVER generate INSERT, UPDATE, DELETE or DROP. Also end the sql query with a semicolon (;) every time without fail.
Use JOINs if needed based on foreign key relationships.
Use mptt concept in user table if the user query is related to user team or user team hierarchy.
User Query: {user_query}
SQL:"""
).partial(schema_text=schema_text)

chain = LLMChain(llm=llm, prompt=prompt)

# --- CHECK IF SQL IS SAFE ---
def is_safe_sql(sql: str) -> bool:
    return bool(re.match(r"(?i)^\s*SELECT\s+", sql.strip()))

# --- EXECUTE SQL SAFELY ---
def execute_sql(query: str):
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                results = [dict(zip(columns, row)) for row in cur.fetchall()]
                return results
    except Exception as e:
        return {"error": str(e)}

import re

def clean_sql(sql: str) -> str:
    # Remove any triple quotes, markdown code fences, or language hints
    sql = re.sub(r"^```[a-z]*", "", sql, flags=re.IGNORECASE)
    sql = sql.replace("```", "")
    sql = sql.replace("'''", "")
    sql = sql.replace('"""', "")
    sql = sql.strip()

    # Only keep up to the first semicolon, as SQL ends there
    if ";" in sql:
        sql = sql.split(";")[0].strip() + ";"

    return sql


# --- MAIN FUNCTION TO RUN QUERY ---
def run_query(user_query: str):
    sql_query = chain.run({"user_query": user_query}).strip()
    clean = clean_sql(sql_query)

    if not is_safe_sql(clean):
        return {"error": "Unsafe query detected. Only SELECT queries are allowed."}

    result = execute_sql(clean)
    return result


# --- TEST ---
if __name__ == "__main__":
    print("🔍 Ask your database a question (CTRL+C to exit)\n")
    while True:
        try:
            user_input = input("You: ")
            output = run_query(user_input)
            print("🧾 Result:\n", json.dumps(output, indent=2, ensure_ascii=False))
        except KeyboardInterrupt:
            print("\nExiting...")
            break
