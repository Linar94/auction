from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .dataclasses import TokenData
from ..settings import SECRET_KEY, ALGORITHM
from ..user.models import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await UserModel.query.where(UserModel.username == token_data.username).gino.first()
    if user is None:
        raise credentials_exception

    return user
