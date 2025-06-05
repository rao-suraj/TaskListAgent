from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.chat_routes import router as chat_router

app = FastAPI(title="Task List Agent API", description="API to chat with Task list agents")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Task list agent API"}