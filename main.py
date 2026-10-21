import os
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import AuthApiError

# Initializing dependencies
load_dotenv()
app = FastAPI()

# Declaring supabase credentials
SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

if SUPABASE_URL is None or SUPABASE_KEY is None:
    print("SUPABASE_URL or SUPABASE_KEY is missing in your .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Creating base models
class AuthRequest(BaseModel):
    email: str
    password: str


@app.get("/")
def index():
    return {"status": "uvicorn is working."}


@app.post("/auth/signup", status_code=201)
def signup(body: AuthRequest):
    if not body.email or not body.email.strip() or not body.password:
        raise HTTPException(
            status_code=400, detail={"error": "Email and password are required."}
        )

    try:
        response = supabase.auth.sign_up(
            {
                "email": body.email,
                "password": body.password,
            }
        )
    except Exception as e:
        print("Failed to verify signup credentials: ", e)
        raise HTTPException(status_code=500, detail={"error": e})

    if response.user is None:
        raise HTTPException(
            status_code=400,
            detail={"error": "Signup failed or email already registered."},
        )

    return response.user


@app.post("/auth/login", status_code=200)
def login(body: AuthRequest):
    if not body.email or not body.email.strip() or not body.password:
        raise HTTPException(
            status_code=400, detail={"error": "Email and password are required."}
        )

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": body.email,
                "password": body.password,
            }
        )
    except AuthApiError as e:
        print("Login rejected by Supabase: ", e)
        raise HTTPException(
            status_code=401, detail={"error": "Invalid login credentials."}
        )

    except Exception as e:
        print("Failed to verify login credentials: ", e)
        raise HTTPException(status_code=500, detail={"error": "Database error."})

    if response.user is None or response.session is None:
        raise HTTPException(
            status_code=500, detail={"error": "Login failed unexpectedly."}
        )

    return {
        "acess_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
    }
