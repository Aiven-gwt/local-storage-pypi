from core.config import settings
import asyncssh


"""синхронные"""
# def run_ssh_command(command: str):
#     """Выполняет команду на удалённом сервере через SSH."""
#     try:
#         result = subprocess.run(
#             ["ssh", f"{settings.SERVER_USER}@{settings.SERVER_IP}", command],
#             capture_output=True,
#             text=True,
#             check=True,
#         )
#         return result.stdout
#     except subprocess.CalledProcessError as e:
#         raise Exception(f"SSH command failed: {e.stderr}")
#
#
# def copy_file_to_linux(local_path: str, remote_path: str):
#     """Копирует файл на удалённый сервер через SCP."""
#     try:
#         subprocess.run(
#             [
#                 "scp",
#                 local_path,
#                 f"{settings.SERVER_USER}@{settings.SERVER_IP}:{remote_path}",
#             ],
#             check=True,
#         )
#     except subprocess.CalledProcessError as e:
#         raise Exception(f"Failed to copy file: {e.stderr}")


"""асинхронные"""


async def run_ssh_command(command: str):
    async with asyncssh.connect(
        settings.SERVER_IP, username=settings.SERVER_USER
    ) as conn:
        result = await conn.run(command)
        if result.exit_status != 0:
            raise Exception(f"SSH command failed: {result.stderr}")
        return result.stdout


async def copy_file_to_linux(local_path: str, remote_path: str):
    async with asyncssh.connect(
        settings.SERVER_IP, username=settings.SERVER_USER
    ) as conn:
        await asyncssh.scp(local_path, (conn, remote_path))


async def list_packages():
    """Возвращает список пакетов в хранилище."""
    result = await run_ssh_command(f"ls {settings.STORAGE_PATH}/simple")
    return result.splitlines()


async def search_package(package_name: str):
    """Ищет пакет по имени."""
    packages = await list_packages()
    return [pkg for pkg in packages if package_name.lower() in pkg.lower()]


async def upload_package(file_path: str):
    """Загружает пакет в хранилище."""
    await copy_file_to_linux(file_path, f"{settings.STORAGE_PATH}/")
    await run_ssh_command(
        f"{settings.DIR2PI_PATH} {settings.STORAGE_PATH}"
    )  # Обновляем индексы


async def delete_package(package_name: str):
    """Удаляет пакет из хранилища."""
    await run_ssh_command(
        f"rm -rf {settings.STORAGE_PATH}/simple/{package_name} {settings.STORAGE_PATH}/{package_name}*"
    )
    await run_ssh_command(
        f"{settings.DIR2PI_PATH} {settings.STORAGE_PATH}"
    )  # Обновляем индексы
