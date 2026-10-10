from fastapi import FastAPI
from database import init_db
from routes_auth import router as auth_router

# Create the server application
app = FastAPI(title ="PrepPilot API")

# Create the database tables when the server starts
init_db()

# Add the signup route to the app
app.include_router(auth_router)

# Test route: open /api/hello to check that the server is running
@app.get("/api/hello")
def hello():
    return {"message":"PrepPilot server is running"}