import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from users.views import router as users_router
from packages.views2 import router as packages_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router=users_router, prefix="/user")
app.include_router(router=packages_router, prefix="/packages")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (для разработки)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home(
    request: Request,
):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "server_ip": os.getenv("SERVER_IP", "127.0.0.1"),
            "server_port": os.getenv("SERVER_PORT", "8000"),
        },
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)
