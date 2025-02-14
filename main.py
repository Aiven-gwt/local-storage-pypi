from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from users.views import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=users_router, prefix="/user")


@app.get("/hello")
async def hello_message():
    return {
        "message": "hello"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
