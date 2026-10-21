import os
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

# Initializing dependencies
load_dotenv()
app = FastAPI()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/")
def index():
    return {"status": "server is working."}


@app.get("/supabase")
def server():
    try:
        return supabase.table("instruments").select("*").execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
