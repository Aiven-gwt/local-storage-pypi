from pydantic import BaseModel


# Модель для создания пользователя
class UserCreate(BaseModel):
    username: str
    password: str


# Модель для ответа с данными пользователя
class UserResponse(BaseModel):
    username: str
    role: str


# Модель для смены роли
class ChangeRoleRequest(BaseModel):
    username: str
    new_role: str


# Модель для удаления пользователя
class DeleteUserRequest(BaseModel):
    username: str


# Модель для изменения пароля
class ChangePasswordRequest(BaseModel):
    username: str
    new_password: str


# Модель для вывода списка пользователей
class SafeUserResponse(BaseModel):
    username: str
    role: str
