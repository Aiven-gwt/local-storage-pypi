from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil

from core.models import User
from packages.helpers import (
    upload_package,
    list_packages,
    search_package,
    delete_package,
)
from users.views import get_current_admin

router = APIRouter(tags=["Storage management"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_package_endpoint(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_admin),
):
    """Загружает пакет в хранилище."""
    temp_path = Path(f"temp/{file.filename}")  # Сохраняем файл во временную директорию
    try:
        # Сохраняем файл во временную директорию
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Пытаемся загрузить пакет в хранилище
        try:
            await upload_package(str(temp_path))
            return JSONResponse(
                content={"message": f"Package {file.filename} uploaded and indexed!"},
            )
        except Exception as e:
            # Ошибка при загрузке пакета в хранилище
            raise HTTPException(status_code=500, detail=f"Failed to upload package: {e}")
    except Exception as e:
        # Ошибка при сохранении файла во временную директорию
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    finally:
        # Удаляем временный файл после завершения операции
        if temp_path.exists():
            temp_path.unlink()


@router.get("/list", response_model=list[str])
async def list_packages_endpoint():
    """Возвращает список пакетов в хранилище."""
    try:
        packages = await list_packages()
        return packages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=list[str])
async def search_package_endpoint(package_name: str):
    """Ищет пакет по имени."""
    try:
        packages = await search_package(package_name)
        return packages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{package_name}", status_code=status.HTTP_200_OK)
async def delete_package_endpoint(
        package_name: str,
        current_user: User = Depends(get_current_admin),
):
    """Удаляет пакет из хранилища."""
    try:
        await delete_package(package_name)
        return {"message": f"Package {package_name} deleted!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
