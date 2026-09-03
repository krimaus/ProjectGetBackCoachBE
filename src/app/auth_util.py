import os
from typing import Annotated
from uuid import UUID

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from pwdlib import PasswordHash
from starlette import status

load_dotenv()

password_hash = PasswordHash.recommended()

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

async def encode_jwt(encode: dict) -> str:
    return jwt.encode(encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> dict:
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        username: str = payload.get('sub')
        raw_id = payload.get('id')

        if username is None or raw_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials'
            )

        try:
            user_id = UUID(raw_id)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials'
            )

        return {'username': username, 'id': user_id}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except JWTError as e:
        print("JWT decode failed:", repr(e))
        raise HTTPException(status_code=401, detail='Could not validate credentials')
        
user_dependency = Annotated[dict, Depends(get_current_user)]