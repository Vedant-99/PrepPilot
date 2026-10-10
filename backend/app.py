import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from database import init_db
from routes_auth import router as auth_router


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

# Test route: open /api/hello to check that the server is running
@app.get("/api/hello")
def hello():
    return {"message":"PrepPilot server is running"}