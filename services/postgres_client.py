from langchain_community.utilities import SQLDatabase
import os

def query_internal_db(query):
    # Connects to your Postgres database using a secret URL
    db = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))
    return db.run(query)