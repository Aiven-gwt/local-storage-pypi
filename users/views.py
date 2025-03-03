from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.models import db_helper, User
from .helpers import (
    get_user,
    create_user,
    verify_password,
    change_user_role,
    change_user_password,
    user_delete,
    get_all_users,
)
from .schemas import (
    UserResponse,
    UserCreate,
    ChangeRoleRequest,
    ChangePasswordRequest,
    DeleteUserRequest,
    SafeUserResponse,
)

router = APIRouter(tags=["auth"])
security = HTTPBasic()


# Проверка пользователя на роль admin
async def get_current_admin(
    credentials: HTTPBasicCredentials = Depends(security),
    db: AsyncSession = Depends(
        db_helper.scoped_session_dependency,
    ),
):
    user = await get_user(db, credentials.username)
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@router.get("/users", response_model=list[SafeUserResponse])
async def get_all_users_endpoint(
    db: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    users = await get_all_users(db)
    return users


# эндпоинт регистрации
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    db_user = await get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    created_user = await create_user(db, user)
    return {"username": created_user.username, "role": created_user.role}


# эндпоинт смены роли
@router.put(
    "/change-role",
    status_code=status.HTTP_200_OK,
)
async def change_role(
    request: ChangeRoleRequest,
    db: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user: User = Depends(get_current_admin),
):
    if request.new_role not in ["admin", "user"]:
        raise HTTPException(
            status_code=400, detail="New role must be either 'admin' or 'user'"
        )

    updated_user = await change_user_role(db, request.username, request.new_role)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": f"Role for user '{request.username}' changed to '{request.new_role}'"
    }


# эндпоинт авторизации
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login(
    credentials: HTTPBasicCredentials = Depends(security),
    db: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    user = await get_user(db, credentials.username)
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"username": user.username, "role": user.role}


# эндпоинт удаления пользователя
@router.delete(
    "/delete",
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    request: DeleteUserRequest,
    db: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user: User = Depends(get_current_admin),
):
    deleted_user = await user_delete(db, request.username)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User '{request.username}' deleted successfully"}


# эндпоинт изменения пароля пользователя
@router.put("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    db: AsyncSession = Depends(db_helper.scoped_session_dependency),
    current_user: User = Depends(get_current_admin),
):
    updated_user = await change_user_password(
        db, request.username, request.new_password
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"Password for user '{request.username}' changed successfully"}
