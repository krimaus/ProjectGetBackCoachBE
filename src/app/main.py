from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import endpoints

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow React app to make requests (update if deployed elsewhere)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(endpoints.users.users_router)
app.include_router(endpoints.practice_router)
app.include_router(endpoints.teams_router)
app.include_router(endpoints.attendance_router)