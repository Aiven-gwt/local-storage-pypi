import asyncio
import os
from zipfile import ZipFile

import aiofiles
from fastapi import HTTPException
from packaging import requirements

from core.config import settings


async def run_local_command(command: str):
    """Выполняет команду в локальной системе."""
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        error_message = stderr.decode().strip()
        print(f"Command failed: {command}")
        print(f"Error: {error_message}")
        raise HTTPException(
            status_code=400, detail=f"Command failed: {stderr.decode()}"
        )
    return stdout.decode()


async def copy_file_locally(local_path: str, destination_path: str):
    """Копирует файл локально."""
    try:
        async with aiofiles.open(local_path, "rb") as src_file:
            async with aiofiles.open(destination_path, "wb") as dest_file:
                await dest_file.write(await src_file.read())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to copy file: {str(e)}")


async def list_packages():
    """Возвращает список пакетов в хранилище."""
    try:
        packages = await asyncio.to_thread(
            os.listdir, f"{settings.STORAGE_PATH}/simple"
        )
        return packages
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to list packages: {str(e)}"
        )


async def search_package(package_name: str):
    """Ищет пакет по имени."""
    packages = await list_packages()
    return [pkg for pkg in packages if package_name.lower() in pkg.lower()]


def extract_metadata_from_whl(whl_path: str) -> dict:
    """Извлекает метаданные из пакета .whl."""
    metadata = {}
    with ZipFile(whl_path, "r") as whl:
        for file in whl.namelist():
            if file.endswith("METADATA") or file.endswith("PKG-INFO"):
                with whl.open(file) as metadata_file:
                    for line in metadata_file:
                        line = line.decode("utf-8").strip()
                        if line.startswith("Requires-Dist:"):
                            dependency = line.split(":", 1)[1].strip()
                            if ";" not in dependency:
                                metadata.setdefault("dependencies", []).append(
                                    dependency
                                )
    return metadata


async def get_installed_package_version(package_name: str) -> str | None:
    """Возвращает версию установленного пакета в локальном хранилище."""
    package_path = os.path.join(settings.STORAGE_PATH, "simple", package_name)
    if os.path.exists(package_path):
        for file in os.listdir(package_path):
            if file.endswith(".whl"):
                parts = file.split("-")
                if len(parts) >= 2:
                    return parts[1]  # Возвращаем версию
    return None


async def check_dependencies_in_local_repo(
    dependencies: list[str],
) -> tuple[bool, list[str]]:
    """Проверяет наличие обязательных зависимостей в локальном хранилище с учетом версий."""
    missing_dependencies = []
    for dependency in dependencies:
        req = requirements.Requirement(dependency)
        package_name = req.name
        installed_version = await get_installed_package_version(package_name)

        if installed_version:
            if not req.specifier.contains(installed_version):
                missing_dependencies.append(
                    f"{package_name} (требуется {dependency}, установлено {installed_version})"
                )
        else:
            missing_dependencies.append(
                f"{package_name} (требуется {dependency}, пакет отсутствует)"
            )

    if missing_dependencies:
        return False, missing_dependencies
    return True, []


async def upload_package(file_path: str):
    """Загружает пакет в хранилище с проверкой зависимостей."""
    try:
        metadata = extract_metadata_from_whl(file_path)
        dependencies = metadata.get("dependencies", [])

        success, missing_deps = await check_dependencies_in_local_repo(dependencies)
        if not success:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Не все зависимости удовлетворены",
                    "missing_dependencies": missing_deps,
                },
            )

        # Копируем файл в хранилище
        destination_path = os.path.join(
            settings.STORAGE_PATH, os.path.basename(file_path)
        )
        await copy_file_locally(file_path, destination_path)

        # Обновляем индексы
        await run_local_command(f"{settings.DIR2PI_PATH} {settings.STORAGE_PATH}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to upload package: {str(e)}"
        )


async def delete_package(package_name: str):
    """Удаляет пакет из хранилища."""
    try:
        # Удаляем пакет и его индексы
        await run_local_command(
            f"rm -rf {settings.STORAGE_PATH}/simple/{package_name} {settings.STORAGE_PATH}/{package_name}*"
        )

        # Обновляем индексы
        await run_local_command(f"{settings.DIR2PI_PATH} {settings.STORAGE_PATH}")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to delete package: {str(e)}"
        )
