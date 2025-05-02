# backend.py
from fastapi import FastAPI
import asyncio
import datetime

app = FastAPI()

count = 0

@app.get("/")
async def read_root():
    global count
    print(datetime.datetime.now() , " => ",count)
    count +=1
    await asyncio.sleep(2)  # Simulate slow I/O
    return {"message": "Hello from FastAPI"}
