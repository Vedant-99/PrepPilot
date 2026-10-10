from fastapi import FastAPI

# Create the server application
app = FastAPI(title ="PrepPilot API")

# Test route: open /api/hello to check that the server is running
@app.get("/api/hello")
def hello():
    return {"message":"PrepPilot server is running"}