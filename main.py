from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from sql_utils import parse_sql_query_response, run_sql_query
from netfree_unstrict_ssl import unstrict_ssl
unstrict_ssl()
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
db_schema = (DATA_DIR / "schema.md").read_text(encoding="utf-8")

@app.get("/")
def hello():
    return {"message": "Hello from Smart Home Agent!"}

@app.post("/api/chat")
async def chat(body: dict):
    question = body.get("question")
    print(f"Received question: {question}")

    sql_system_prompt = f"""אתה עוזר לניסוח ותכנון שאילתות SQL על בסיס סכמה נתונה של מסד נתונים.
    
    סכמת מסד נתונים:
    {db_schema}
    
    צור שאילתת SQL לשליפת המידע הנדרש כדי לענות לשאלה הבאה:
    {question}
    
    החזר את התשובה בפורמט JSON בלבד, ללא הוספת שום תו נוסף, במבנה הבא:
    {{
        "sql_query": "generated validated sql query based on DB schema"
    }}
    """
    
    sql_query_response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=[{"role":"system", "content":sql_system_prompt}],
        max_completion_tokens=1000,
        temperature=0.5,
        timeout=30.0
    )

    sql_query = parse_sql_query_response(sql_query_response)
    print(sql_query)
    data = run_sql_query(sql_query)

    system_prompt = f"""אתה מערכת ניהול חכמה של רובוטים ביתיים. ענה על שאלות המשתמש בהתבסס על הנתונים הבאים ממסד הנתונים.
    השתמש בעברית תקנית. אם התשובה לא נמצאת בנתונים, אמור שאין לך מספיק מידע.
    
    נתונים:
    {data}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]
        
    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=messages,
        max_completion_tokens=1000,
        temperature=0.5,
        timeout=30.0
    )

    answer = response.choices[0].message.content

    return {"answer":answer,
            "success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8050)
