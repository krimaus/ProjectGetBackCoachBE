from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_session
from src.app.service_layer.pydantic_models.auth import Token
from src.app.service_layer.services.auth.service import authenticate_user


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/token",
    response_model=Token
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session)
):
    return await authenticate_user(session, form_data.username, form_data.password)