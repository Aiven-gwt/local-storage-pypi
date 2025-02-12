import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/hello")
async def hello_message():
    return {
        "message": "hello"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
