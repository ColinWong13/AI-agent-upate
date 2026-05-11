from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.user import User, UserFavorite, UserNote
from auth import hash_password, verify_password, create_token, current_user, require_user

router = APIRouter(prefix="/api/user", tags=["user"])


# -- schemas --

class RegisterBody(BaseModel):
    email: str
    password: str
    nickname: str

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("请输入有效邮箱")
        return v.strip().lower()

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("密码至少 8 个字符")
        return v

    @field_validator("nickname")
    @classmethod
    def nickname_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 20:
            raise ValueError("昵称需 2-20 个字符")
        return v


class LoginBody(BaseModel):
    email: str
    password: str


class FavoriteBody(BaseModel):
    item_type: str
    item_id: int


class NoteBody(BaseModel):
    item_type: str
    item_id: int
    content: str


# -- auth routes --

@router.post("/register", status_code=201)
async def register(body: RegisterBody, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User.id).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="该邮箱已被注册")
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        nickname=body.nickname,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_token(user.id)
    return {"access_token": token, "nickname": user.nickname}


@router.post("/login")
async def login(body: LoginBody, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email.strip().lower()))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token = create_token(user.id)
    return {"access_token": token, "nickname": user.nickname}


@router.get("/me")
async def me(user: User = Depends(require_user)):
    return {"id": user.id, "email": user.email, "nickname": user.nickname}


# -- favorites routes --

@router.get("/favorites")
async def list_favorites(
    item_type: str | None = None,
    user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(UserFavorite).where(UserFavorite.user_id == user.id)
    if item_type:
        q = q.where(UserFavorite.item_type == item_type)
    q = q.order_by(UserFavorite.created_at.desc())
    result = await db.execute(q)
    return [
        {"id": f.id, "item_type": f.item_type, "item_id": f.item_id, "created_at": f.created_at.isoformat()}
        for f in result.scalars().all()
    ]


@router.post("/favorites", status_code=201)
async def add_favorite(body: FavoriteBody, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(UserFavorite.id).where(
            UserFavorite.user_id == user.id,
            UserFavorite.item_type == body.item_type,
            UserFavorite.item_id == body.item_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="已收藏")
    fav = UserFavorite(user_id=user.id, item_type=body.item_type, item_id=body.item_id)
    db.add(fav)
    await db.commit()
    return {"id": fav.id}


@router.delete("/favorites/{fav_id}")
async def remove_favorite(fav_id: int, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserFavorite).where(UserFavorite.id == fav_id, UserFavorite.user_id == user.id))
    fav = result.scalar_one_or_none()
    if fav is None:
        raise HTTPException(status_code=404, detail="收藏不存在")
    await db.delete(fav)
    await db.commit()
    return {"deleted": fav_id}


# -- notes routes --

@router.get("/notes")
async def list_notes(user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserNote).where(UserNote.user_id == user.id).order_by(UserNote.updated_at.desc())
    )
    return [
        {"id": n.id, "item_type": n.item_type, "item_id": n.item_id, "content": n.content,
         "created_at": n.created_at.isoformat(), "updated_at": n.updated_at.isoformat()}
        for n in result.scalars().all()
    ]


@router.post("/notes", status_code=201)
async def save_note(body: NoteBody, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    if len(body.content) > 5000:
        raise HTTPException(status_code=422, detail="笔记不能超过 5000 字")
    result = await db.execute(
        select(UserNote).where(
            UserNote.user_id == user.id,
            UserNote.item_type == body.item_type,
            UserNote.item_id == body.item_id,
        )
    )
    note = result.scalar_one_or_none()
    if note:
        note.content = body.content
    else:
        note = UserNote(user_id=user.id, item_type=body.item_type, item_id=body.item_id, content=body.content)
        db.add(note)
    await db.commit()
    await db.refresh(note)
    return {"id": note.id, "content": note.content}


@router.delete("/notes/{note_id}")
async def delete_note(note_id: int, user: User = Depends(require_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserNote).where(UserNote.id == note_id, UserNote.user_id == user.id))
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    await db.delete(note)
    await db.commit()
    return {"deleted": note_id}
