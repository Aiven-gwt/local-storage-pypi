from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi import status
from pathlib import Path
import aiofiles
import aiofiles.os as aio_os
from core.models import User
from packages.helpers2 import (
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
        # Создаём временную директорию, если её нет
        await aio_os.makedirs("temp", exist_ok=True)

        # Сохраняем файл во временную директорию асинхронно
        async with aiofiles.open(temp_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)

        # Пытаемся загрузить пакет в хранилище
        try:
            await upload_package(str(temp_path))
            return JSONResponse(
                content={"message": f"Package {file.filename} uploaded and indexed!"},
            )
        except HTTPException as e:
            # Ошибка при загрузке пакета в хранилище
            if e.detail.get("missing_dependencies"):
                return JSONResponse(
                    status_code=e.status_code,
                    content={
                        "message": e.detail["message"],
                        "missing_dependencies": e.detail["missing_dependencies"],
                    },
                )
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to upload package: {e}"
            )
    except Exception as e:
        # Ошибка при сохранении файла во временную директорию
        raise HTTPException(status_code=500, detail="Failed to save file")
    finally:
        # Удаляем временный файл после завершения операции
        if await aio_os.path.exists(temp_path):
            await aio_os.remove(temp_path)


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
