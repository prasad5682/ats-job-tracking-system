from fastapi import FastAPI

app = FastAPI(title="ATS Job Application API")

@app.get("/")
def root():
    return {"message": "ATS API is running successfully"}
