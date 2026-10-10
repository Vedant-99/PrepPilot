from fastapi import FastAPI
from database import init_db

# Create the server application
app = FastAPI(title ="PrepPilot API")

# Create the database tables when the server starts
init_db()


# Test route: open /api/hello to check that the server is running
@app.get("/api/hello")
def hello():
    return {"message":"PrepPilot server is running"}