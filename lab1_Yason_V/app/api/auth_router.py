from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app import schemas, crud, auth
from app.deps import get_db, get_current_user
from app.cache_service import cache_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.Token)
def register(user_in: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = crud.create_user(db, user_in)
    
    access_token = auth.create_access_token(data={"user_id": user.id})
    refresh_token = auth.create_refresh_token()
    
    user_agent = request.headers.get("user-agent")
    session_data = {
        "user_id": user.id,
        "user_agent": user_agent,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }
    
    cache_service.set_session(refresh_token, session_data)
    cache_service.add_user_session(user.id, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, request: Request, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, user_in.email)
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not auth.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = auth.create_access_token(data={"user_id": user.id})
    refresh_token = auth.create_refresh_token()
    
    user_agent = request.headers.get("user-agent")
    session_data = {
        "user_id": user.id,
        "user_agent": user_agent,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }
    
    cache_service.set_session(refresh_token, session_data)
    cache_service.add_user_session(user.id, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(refresh_request: schemas.RefreshTokenRequest, request: Request, db: Session = Depends(get_db)):
    payload = auth.decode_token(refresh_request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    session = cache_service.get_session(refresh_request.refresh_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    access_token = auth.create_access_token(data={"user_id": session["user_id"]})
    new_refresh_token = auth.create_refresh_token()
    
    cache_service.delete_session(refresh_request.refresh_token)
    cache_service.remove_user_session(session["user_id"], refresh_request.refresh_token)
    
    user_agent = request.headers.get("user-agent")
    new_session_data = {
        "user_id": session["user_id"],
        "user_agent": user_agent,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
    }
    
    cache_service.set_session(new_refresh_token, new_session_data)
    cache_service.add_user_session(session["user_id"], new_refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout(refresh_request: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    session = cache_service.get_session(refresh_request.refresh_token)
    if session:
        cache_service.delete_session(refresh_request.refresh_token)
        cache_service.remove_user_session(session["user_id"], refresh_request.refresh_token)
    return {"message": "Successfully logged out"}

@router.post("/logout-all")
def logout_all(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cache_service.delete_all_user_sessions(current_user.id)
    return {"message": "Successfully logged out from all devices"}

@router.get("/sessions", response_model=list[schemas.SessionRead])
def get_my_sessions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions_tokens = cache_service.get_user_sessions(current_user.id)
    sessions = []
    
    for i, token in enumerate(sessions_tokens):
        session_data = cache_service.get_session(token)
        if session_data:
            sessions.append({
                "id": i + 1,
                "user_agent": session_data.get("user_agent"),
                "created_at": datetime.fromisoformat(session_data["created_at"]),
                "expires_at": datetime.fromisoformat(session_data["expires_at"])
            })
    
    return sessions

@router.get("/github/login") 
async def github_login():
    with auth.github_sso:
        return await auth.github_sso.get_login_redirect()

@router.get("/github/callback", response_model=schemas.Token)
async def github_callback(request: Request, db: Session = Depends(get_db)):
    with auth.github_sso:
        user_info = await auth.github_sso.verify_and_process(request)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
        
        user = crud.get_user_by_github_id(db, user_info.id)
        
        if not user:
            user_data = schemas.UserOAuthCreate(
                name=user_info.display_name or user_info.email.split('@')[0],
                email=user_info.email,
                github_id=user_info.id
            )
            user = crud.create_oauth_user(db, user_data)
        
        access_token = auth.create_access_token(data={"user_id": user.id})
        refresh_token = auth.create_refresh_token()
        
        user_agent = request.headers.get("user-agent")
        session_data = {
            "user_id": user.id,
            "user_agent": user_agent,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        cache_service.set_session(refresh_token, session_data)
        cache_service.add_user_session(user.id, refresh_token)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }