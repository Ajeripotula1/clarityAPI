from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session # Session manager for DB ops
from database import get_db
from db_models import User
import jwt
from jwt.exceptions import InvalidTokenError
from models.schema import UserCreate, UserResponse, Token
from pwdlib import PasswordHash # Argon password hashing 
from datetime import datetime, timedelta, timezone
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

#### Token Utilities ####
SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Extract Token from request to auth/token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def create_access_token(data: dict):
    to_encode = data.copy() # copy the dict 
    # calculate the expirary time 
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # add expiration time to payload
    to_encode.update({"exp":expire})
    # encode/ sign payload w/ secret key and algorithm 
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm = ALGORITHM
    )
    return encoded_jwt

# Determine the identity of the current user based on token in request
def get_current_user(token: str = Depends(oauth2_scheme)):
     # Build Credentials Exception
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try: 
        # decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        print(f"🔍 DEBUG: Decoded payload: {payload}")
        # extract the user id (sub)
        user_id = payload.get("sub")
        if user_id is None:
            print("❌ DEBUG: user_name is None!")
            raise credentials_exception
    
    except InvalidTokenError as e:
        print(f"❌ DEBUG: Token decode error: {e}")
        raise credentials_exception
    # success, return username to query later on 
    return user_id

# test the protected route
@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return current_user

#### Password Hashing Utilities ####

# Hasher for plaintext 
password_hash = PasswordHash.recommended()

# generate hashed password 
def get_password_hash(plain_password:str):
    return password_hash.hash(plain_password)

# Verify hashed password 
def verify_password(plain_password:str, hashed_password:str): 
    return password_hash.verify(plain_password, hashed_password)


# Helper function to retrieve User from Database
def get_user(db, username):
    return db.query(User).filter(User.username == username).first()

#### Authentication and Authorization ####

# Register a new user
# input: username and password
# return: user info 
@router.post('/register', response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends (get_db)):
    # check if username is unique (get user function)
    db_user = get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists, please pick another.")
    # hash password
    hashed_password = get_password_hash(user.password)
    # create unique ID for user 
    # create new User python obj model
    new_user = User(
        id=str(uuid.uuid4()), 
        username=user.username, 
        password=hashed_password
    ) 
    print(new_user)
    # add to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
    
def authenticate_user(db, username:str, password:str):
    """
    Verify user credentials against DB entry
    """
    # Locate user in table 
    user = get_user(db, username)
    if not user:
        return False
    # Verify hashed password
    if not verify_password(password, user.password):
        return False 
    
    # Return User DB Instance 
    return user 

# Login a user
# input: username and password
# return: JWT Token to access protected routes 
@router.post('/token', response_model=Token)
async def login(form_data:OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    # lookup username in DB (get user function)
    db_user = authenticate_user(db,form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={"WWW-Authenticate": "Bearer"},
        )
    # user is authenticated, create and assign JWT Token 
    print('creating token for ', db_user.username, db_user.id)
    access_token = create_access_token(data={"sub": db_user.id})
    return Token(access_token=access_token, token_type='bearer')
