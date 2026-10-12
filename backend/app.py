import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from database import init_db
from routes_auth import router as auth_router
from routes_profile import router as profile_router

# The frontend folder is next to the backend folder
FRONTEND_DIR = Path(__file__).parent.parent/"frontend"


# Create the server application
app = FastAPI(title ="PrepPilot API")

# Create the database tables when the server starts
init_db()

# Sessions: a signed cookie remembers who is logged in (valid for 7 days)
# On a real server, set the long random SECRET_KEY enviornment variable
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECCRET_KEY","dev-secret-change-me"),
    max_age = 60*60*24*7,
    same_site = "lax"
)

# Add the signup and login route to the app
app.include_router(auth_router)

# Add profile route to the app
app.include_router(profile_router)

# Test route: open /api/hello to check that the server is running
@app.get("/api/hello")
def hello():
    return {"message":"PrepPilot server is running"}

#  Serve the website pages (index.html, login.html .....)
app.mount("/",StaticFiles(directory=FRONTEND_DIR, html=True), name ="frontend")
