from fastapi import FastAPI
from app.routers import auth_router, chat_router

app = FastAPI(title="OtakuBhai API")

app.include_router(auth_router.auth_router)
app.include_router(chat_router.chat_router)