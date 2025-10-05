import pandas as pd
import os
import urllib.parse
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.utilities import SQLDatabase
from sqlalchemy import inspect
from dotenv import load_dotenv


load_dotenv() 

# ---------------- Database Configuration ----------------
db_user = os.getenv("NEON_DB_USER")
db_password = urllib.parse.quote_plus(os.getenv("NEON_DB_PASSWORD"))
db_host = os.getenv("NEON_DB_HOST")
db_port = os.getenv("NEON_DB_PORT", "5432")  
db_name = os.getenv("NEON_DB_NAME")

# PostgreSQL connection URI format for SQLAlchemy
db_uri = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

# Create SQLAlchemy engine for PostgreSQL NeonDB
engine = create_engine(db_uri)

# Initialize SQLDatabase (langchain wrapper)
db = SQLDatabase(engine, sample_rows_in_table_info=3)

# ---------------- LLM Configuration ----------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.environ["GOOGLE_API_KEY"],
    temperature=0,
)

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="SQL Question Answering", layout="wide")
st.title("Prompt2SQL 🍴 (Foodie Q/A App)")

# Sidebar for table scope selection
st.sidebar.header("Filter by Place")
inspector = inspect(engine)
places = sorted(inspector.get_table_names())
selected_place = st.sidebar.selectbox("Select a place (table)", places)

question = st.text_input("Enter your question:")

# ---------------- Helper Function ----------------

def generate_sql_and_execute(question, selected_table="All"):
    try:
        # Build prompt with properly indented multi-line string
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are a SQL expert assistant. Given the following database schema, generate accurate PostgreSQL queries to answer user questions. "
             "Always verify the schema before generating queries:\n"
             "- Table with columns:\n"
             "  - name (Names of restaurants/dining/food places.)\n"
             "  - price (Average food price at the place.)\n"
             "  - cusine_category (Comma-separated cuisine types, e.g., 'South Indian, North Indian, Italian'.)\n"
             "  - city (Name of the city.)\n"
             "  - region (Specific locality or area in the city.)\n"
             "  - url (Zomato app link for the restaurant.)\n"
             "  - page_no (Pagination info from Zomato listings)\n"
             "  - cusine_type (Type of establishment e.g. Microbrewery, Casual Dining, Bar, Pub, Bakery, Quick Bites, Dessert Parlor)\n"
             "  - timing (Opening hours with day specifics, e.g., '12noon to 11:30pm(Mon,Tue,Wed,Thu,Sun)')\n"
             "  - rating_type (Qualitative rating like Very Good, Good, Excellent, Average)\n"
             "  - rating (Numeric rating of the place)\n"
             "  - votes (Number of ratings received)\n\n"
             "Answer user questions with accurate SQL queries. If the question asks for 'South Indian food in Bengaluru', "
             "check the 'cusine_category' column for '%South Indian%' etc.\n\n"
             "Examples:\n"
             "Q: Recommend me some best Casual Dining places in Bengaluru.\n"
             "A: SELECT name, rating_type, cusine_type FROM bengaluru WHERE cusine_type LIKE '%Casual Dining%' ORDER BY rating DESC LIMIT 5;\n\n"
             "Q: List Casual Dining Italian places with average price below 500\n"
             "A: SELECT name, price, cusine_type, cusine_category FROM bengaluru\n"
             "WHERE cusine_type LIKE '%Casual Dining%'\n"
             "AND cusine_category LIKE '%Italian%'\n"
             "AND price < 500;\n\n"
             "Q: Show bakeries in Indiranagar with excellent rating type\n"
             "A: SELECT name, region, rating_type FROM bengaluru\n"
             "WHERE cusine_type LIKE '%Bakery%'\n"
             "AND region = 'Indiranagar'\n"
             "AND rating_type = 'Excellent';\n\n"
             "Q: Find pubs open on Fridays with rating above 4.0.\n"
             "A: SELECT name, timing, rating FROM bengaluru\n"
             "WHERE cusine_type LIKE '%Pub%'\n"
             "AND timing LIKE '%Fri%'\n"
             "AND rating > 4.0;\n\n"
             "Common Mistakes to Avoid:\n"
             "- Referencing non-existing columns like address or location unless present.\n"
             "- Using equality = instead of LIKE for cusine_category, which holds comma-separated values.\n"
             "- Ignoring filtering by city or region when user specifies location.\n"
             "- Misinterpreting timing formatting; use pattern matching to handle days.\n"
             "- Confusing cusine_type (establishment category) with cusine_category (food styles).\n\n"
             "Always generate syntactically valid SQL queries respecting the schema and user intent. "
             "When Location is not specified then consider all the tables to answer and do also provide the city column and region column in the output. "
             "Include the URL column for every recommendation so users can access the Zomato page directly."
             "region column sometimes will be a slight different so try to fetch always %region_name% from region column if user asked for a specific region."
             "Provide clear and concise queries using appropriate filters and orderings."
            ),
            ("human", "{question}")
        ])

        
        # If a table/place is selected, narrow down question
        if selected_table != "All":
            question = f"Only query the table '{selected_table}' for: {question}"
        
        formatted_prompt = prompt.format(question=question)
        
        # Invoke LLM
        response = llm.invoke(formatted_prompt)
        sql_text = response.content  # extract string
        
        # Clean SQL
        cleaned_query = sql_text.strip("```sql\n").strip("\n```")
        
        # Execute SQL
        result = db.run(cleaned_query)
        
        return cleaned_query, result
    
    except ProgrammingError as e:
        st.error(f"SQL execution error: {e}")
        return None, None
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

# ---------------- Execute Query ----------------
if st.button("Execute"):
    if question:
        cleaned_query, query_result = generate_sql_and_execute(question, selected_place)
        
        if cleaned_query:
            st.write("Generated SQL Query:")
            st.code(cleaned_query, language="sql")
            
            if query_result:
                if isinstance(query_result, tuple):
                    query_result = [query_result]
                elif isinstance(query_result, str):
                    st.write("Query result:")
                    st.write(query_result)
                    query_result = None

                if query_result:
                    df = pd.DataFrame(query_result)
                    st.write("Query Result:")
                    st.dataframe(df)
            else:
                st.write("No data returned for this query.")
        else:
            st.write("Failed to generate a SQL query.")
    else:
        st.write("Ask Your Query Please")
