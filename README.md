# Prompt2SQL 🚀  
**An AI-powered app that turns natural language into SQL queries**  
Easily query your databases by simply asking questions in plain English. Supports multiple databases, seamless query execution, and a clean interface for instant insights.  [App Link](https://sannidhyadas-prompt2sql.streamlit.app/)


![App Interface](https://github.com/SannidhyaDas/Prompt2Sql/blob/main/App_Interface.png)


---

## ✨ Key Highlights  

- 🔹 Convert **natural language → SQL** instantly  
- 🔹 Works with **PostgreSQL, MySQL, SQLite**, and more  
- 🔹 **User-friendly UI** built with Streamlit  
- 🔹 Powered by **LLMs** for accurate query generation  
- 🔹 Preview and run SQL queries directly on your data  
- 🔹 Can be extended to domain-specific chatbots (e.g., food, e-commerce, finance)  

👨‍💻 Perfect for analysts, developers, product teams, and businesses who want to make data access as simple as asking a question.  

---

## 🎯 Objective  

This project uses the **[Zomato restaurants](https://www.kaggle.com/datasets/ronidas39/zomato-india-data-set) dataset from Kaggle** to demonstrate how non-technical users can ask simple queries and receive:  

- Relevant SQL queries generated automatically  
- Meaningful recommendations in plain English  
- Direct links to ordering platforms or restaurant pages  

In other words: it’s like having a **personal data assistant** for restaurants. Users can ask:  
> *“Where can I get biryani near me at 11 pm?”*  
and instantly get the best options available.  

---

## 💼 Business Use Cases  

Prompt2SQL can be adapted to solve multiple real-world problems:  

1. **Customer Support Chatbots**  
   - Transform user queries into database lookups (e.g., order status, product availability).  
   - Reduces dependency on customer care agents.  

2. **Food Delivery & Restaurant Discovery**  
   - Users can ask for cuisines, timings, ratings, or locations in natural language.  
   - Personalized recommendations without complex filtering.  

3. **E-commerce Search & Recommendation**  
   - Shoppers can type *“Show me red sneakers under ₹3000 with 4+ stars”*.  
   - SQL is generated, fetching results directly from the catalog database.  

4. **Business Intelligence (BI) & Analytics**  
   - Non-technical managers can ask: *“Show last quarter revenue by region”*.  
   - Eliminates the need to write SQL or wait for analysts.  

5. **Finance & Banking**  
   - Customers ask: *“Show my last 5 transactions over ₹10,000”*.  
   - SQL pulls data securely from their banking database.  

---

## 🧪 Examples  

**Q:** Want to have some biryani for dinner, show some places open at 11pm  
**A:**  
```text
[('Hotel Hyderabad Chicken & Beef Biryani House', 'https://www.zomato.com/hyderabad/hotel-hyderabad-chicken-beef-biryani-house-chanda-nagar/info'),
 ('The Village Food Court', 'https://www.zomato.com/hyderabad/the-village-food-court-suraram/info'),
 ('Dabbawala Biryani', 'https://www.zomato.com/hyderabad/dabbawala-biryani-madhapur/info'),
 ... ]
```
**Q:** Currently I'm in Park Street and want to have the best Chinese dishes, show some options

**A:**  
```text
[('Mamagoto', 'Excellent', '4.7', 'https://www.zomato.com/kolkata/mamagoto-park-street-area/info'),
 ('BarBQ', 'Very Good', '4.4', 'https://www.zomato.com/kolkata/barbq-park-street-area/info'),
 ('Aaira', 'Very Good', '4.4', 'https://www.zomato.com/kolkata/aaira-park-street-area/info'),
 ... ]
```

## ⚙️ Environment Setup

Install dependencies:
```{bash}
pip install -r requirements.txt
```

## 🔑 API Key Setup

Get a Gemini API Key → [Gemini Pro](https://ai.google.dev/gemini-api/docs/api)

Set it as an environment variable:
```text
GOOGLE_API_KEY="your_api_key"
```

### 🗄️ Database Setup  

- [MySQL](https://dev.mysql.com/downloads/installer/)  
- [MySQL Workbench](https://dev.mysql.com/downloads/workbench/)  
- [Neon Serverless Postgres (Cloud DB alternative)](https://neon.com/)  

For local development, I first used **MySQL** with a Streamlit app on localhost.  
For deployment, I switched to **Neon DB** as a cloud-based database alternative.  

---

### 🚀 Roadmap to Use as a Product at Scale  

- Add support for schema understanding & auto-joins  
- Deploy as **FastAPI + Docker** microservice  
- Add **authentication & role-based query access**  
- Extend to **finance / e-commerce datasets**  
