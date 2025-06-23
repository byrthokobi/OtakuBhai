from fastapi import APIRouter, HTTPException
from app.models.users import UserRegister, UserInDB, UserLogin
from app.db.mongo import users_collection
from app.auth.hash_handler import hash_password, verify_password
from app.auth.jwt_handler import create_access_token

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/register")
def register_user(user: UserRegister):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)
    user_dict = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_pwd
    }

    users_collection.insert_one(user_dict)

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@auth_router.post("/login")
def login_user(user: UserLogin):
    existing_user = users_collection.find_one({"email": user.email})

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, existing_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}