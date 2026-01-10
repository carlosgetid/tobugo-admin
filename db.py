import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """
    Establishes a connection to the database using SQLAlchemy.
    Returns the engine object.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        st.error("⚠️ DATABASE_URL not found in environment variables. Please check your .env file.")
        return None
    
    try:
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        st.error(f"❌ Failed to connect to database: {e}")
        return None

def load_data(query):
    """
    Executes a SQL query and returns the result as a Pandas DataFrame.
    """
    engine = get_db_connection()
    if engine:
        try:
            with engine.connect() as conn:
                df = pd.read_sql(text(query), conn)
                return df
        except Exception as e:
            st.error(f"❌ Error executing query: {e}")
            return None
    return None
