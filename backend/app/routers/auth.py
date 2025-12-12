from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from app.core import security
from app.core.config import settings
from app.core.database import get_database
from app.models.user import User, UserCreate, Token, UserInDB

router = APIRouter()

@router.post("/register", response_model=User, summary="Register a new user", description="Creates a new user account with the provided username and password. Returns the created user object. Used to onboard new users to the platform.")
async def register(user_in: UserCreate, db=Depends(get_database)):
    # Check if user exists
    user = await db["users"].find_one({"username": user_in.username})
    if user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Hash password
    hashed_password = security.get_password_hash(user_in.password)
    user_db = UserInDB(
        **user_in.dict(), 
        hashed_password=hashed_password
    )
    
    # Insert
    new_user = await db["users"].insert_one(user_db.dict())
    created_user = await db["users"].find_one({"_id": new_user.inserted_id})
    return User(**created_user)

@router.post("/login", response_model=Token, summary="Login for access token", description="Authenticates a user using username and password (OAuth2 form). Returns a JWT access token and a refresh token. Required to authenticate for protected endpoints.")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_database)):
    # Verify user
    user = await db["users"].find_one({"username": form_data.username})
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user["username"]}
    )
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token, summary="Refresh access token", description="Uses a valid refresh token to obtain a new access token. Use this to maintain a session (get new access tokens) without requiring the user to re-login.")
async def refresh_token(refresh_token: str = Body(..., embed=True)):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "refresh":
             raise HTTPException(status_code=401, detail="Invalid refresh token")
             
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        # Rotate refresh token? Optional but good practice. For now just return access.
        # User requested access and refresh tokens. I'll return a new access token.
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token, # Keep same refresh token or rotate
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
