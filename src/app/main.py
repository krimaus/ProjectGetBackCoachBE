from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.communications_layer import endpoints

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(endpoints.attendance_router)
app.include_router(endpoints.auth_router)
app.include_router(endpoints.practice_router)
app.include_router(endpoints.teams_router)
app.include_router(endpoints.users_router)