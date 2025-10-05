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
db_user = "root"
db_password = urllib.parse.quote_plus("put_your_password")  # encode special chars
db_host = "localhost"
db_name = "zomato"

# Create SQLAlchemy engine
engine = create_engine(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}")

# Initialize SQLDatabase
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

# Input question
question = st.text_input("Enter your question:")

# ---------------- Helper Function ----------------

def generate_sql_and_execute(question, selected_table="All"):
    try:
        # Build prompt with properly indented multi-line string
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are a SQL expert assistant. Given the following database schema, generate accurate MySQL queries to answer user questions. "
             "Always verify the schema before generating queries:\n"
             "- Table with columns:\n"
             "  - NAME (Names of restaurants/dining/food places.)\n"
             "  - PRICE (Average food price at the place.)\n"
             "  - CUSINE_CATEGORY (Comma-separated cuisine types, e.g., 'South Indian, North Indian, Italian'.)\n"
             "  - CITY (Name of the city.)\n"
             "  - REGION (Specific locality or area in the city.)\n"
             "  - URL (Zomato app link for the restaurant.)\n"
             "  - PAGE NO (Pagination info from Zomato listings)\n"
             "  - CUSINE TYPE (Type of establishment e.g. Microbrewery, Casual Dining, Bar, Pub, Bakery, Quick Bites, Dessert Parlor)\n"
             "  - TIMING (Opening hours with day specifics, e.g., '12noon to 11:30pm(Mon,Tue,Wed,Thu,Sun)')\n"
             "  - RATING_TYPE (Qualitative rating like Very Good, Good, Excellent, Average)\n"
             "  - RATING (Numeric rating of the place)\n"
             "  - VOTES (Number of ratings received)\n\n"
             "Answer user questions with accurate SQL queries. If the question asks for 'South Indian food in Bengaluru', "
             "check the 'CUSINE_CATEGORY' column for '%South Indian%' etc.\n\n"
             "Examples:\n"
             "Q: Recommend me some best Casual Dining places in Bengaluru.\n"
             "A: SELECT NAME, RATING_TYPE, CUSINE TYPE FROM bengaluru WHERE CUSINE TYPE LIKE '%Casual Dining%' ORDER BY rating DESC LIMIT 5;\n\n"
             "Q: List Casual Dining Italian places with average price below 500\n"
             "A: SELECT NAME, PRICE, CUSINE TYPE, CUSINE_CATEGORY FROM bengaluru\n"
             "WHERE CUSINE TYPE LIKE '%Casual Dining%'\n"
             "AND CUSINE_CATEGORY LIKE '%Italian%'\n"
             "AND PRICE < 500;\n\n"
             "Q: Show bakeries in Indiranagar with excellent rating type\n"
             "A: SELECT NAME, REGION, RATING_TYPE FROM bengaluru\n"
             "WHERE CUSINE TYPE LIKE '%Bakery%'\n"
             "AND REGION = 'Indiranagar'\n"
             "AND RATING_TYPE = 'Excellent';\n\n"
             "Q: Find pubs open on Fridays with rating above 4.0.\n"
             "A: SELECT NAME, TIMING, RATING FROM bengaluru\n"
             "WHERE CUSINE TYPE LIKE '%Pub%'\n"
             "AND TIMING LIKE '%Fri%'\n"
             "AND RATING > 4.0;\n\n"
             "Common Mistakes to Avoid:\n"
             "- Referencing non-existing columns like address or location unless present.\n"
             "- Using equality = instead of LIKE for CUSINE_CATEGORY, which holds comma-separated values.\n"
             "- Ignoring filtering by city or region when user specifies location.\n"
             "- Misinterpreting TIMING formatting; use pattern matching to handle days.\n"
             "- Confusing CUSINE TYPE (establishment category) with CUSINE_CATEGORY (food styles).\n\n"
             "- don't confuse CUSINE TYPE with CUSINE_TYPE, Only CUSINE TYPE is present in tables.\n\n"
             "Always generate syntactically valid SQL queries respecting the schema and user intent. "
             "When Location is not specified then consider all the tables to answer and do also provide the CITY column and REGION column in the output. "
             "Include the URL column for every recommendation so users can access the Zomato page directly."
             "REGION column sometimes will be a slight different so try to fetch always %region_name% from REGION column if user asked for a specific region."
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
                # Convert the result to a pandas DataFrame
                if isinstance(query_result, tuple):
                    query_result = [query_result]  # Wrap single tuple in list
                elif isinstance(query_result, str):
                    # If the result is a string, just display it
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
        st.write("Ask Your Querry Please")        