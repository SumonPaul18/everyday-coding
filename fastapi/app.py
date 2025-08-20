from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello from FastAPI!"}

@app.get("/hello")
def say_hello():
    return {"detail": "হ্যালো বিশ্ব!"}