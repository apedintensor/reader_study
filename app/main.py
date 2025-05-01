from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Reader Study API is live"}