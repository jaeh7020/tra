import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import LinkNonce, User
from app.schemas import Token, UserCreate, UserLogin, UserOut
from app.utils.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@router.post("/register", response_model=Token)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, hashed_password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        line_linked=current_user.line_user_id is not None,
        created_at=current_user.created_at,
    )


@router.get("/link-line")
def link_line(
    linkToken: str = Query(...),
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    LINE account linking endpoint (step 4 of the flow).
    User arrives here from the frontend with their JWT token as a query param.
    We generate a nonce, store it, and redirect to LINE's accountLink endpoint.
    """
    # Verify JWT from query param
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    # Generate a secure nonce
    nonce = secrets.token_urlsafe(32)

    # Store nonce → user mapping
    link_nonce = LinkNonce(nonce=nonce, user_id=user.id)
    db.add(link_nonce)
    db.commit()

    # Redirect to LINE's account linking endpoint
    return RedirectResponse(
        url=f"https://access.line.me/dialog/bot/accountLink?linkToken={linkToken}&nonce={nonce}"
    )


@router.get("/link-line-page")
def link_line_page(linkToken: str = Query(...)):
    """
    Redirect to the frontend login page with the linkToken.
    Users who aren't logged in land here first.
    """
    return RedirectResponse(
        url=f"{settings.APP_URL}/link-line?linkToken={linkToken}"
    )
