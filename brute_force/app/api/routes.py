from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.schemas.user import UserCreate, UserRead, Token
from app.cruds.user import create_user, get_user_by_email
from app.services.auth import verify_password, create_access_token
from app.utils.bruteforce import brute_force_password

from fastapi import UploadFile, File
import subprocess
import os
import uuid

router = APIRouter()

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Регистрация пользователя
@router.post("/sign-up/", response_model=UserRead)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user)

# Логин пользователя
@router.post("/login/", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Брутфорс-подбор пароля
@router.post("/bruteforce/")
def brute_force(target_password: str):
    result = brute_force_password(target_password)
    return {"cracked_password": result}

from app.schemas.task import BruteforceRequest, TaskCreateResponse, TaskStatusResponse
from app.tasks.manager import create_task, get_task
from app.tasks.worker import brute_force_task
from fastapi import BackgroundTasks

from app.tasks.worker import brute_force_task

@router.post("/brut_hash", response_model=TaskCreateResponse)
def bruteforce_start(request: BruteforceRequest):
    task_id = create_task()
    brute_force_task.delay(
        task_id,
        request.hash,
        request.charset,
        min(request.max_length, 8),
        request.mode
    )
    return {"task_id": task_id}

#эндпоинт для получения статуса задачи
@router.get("/get_status", response_model=TaskStatusResponse)
def get_status(task_id: str):
    task = get_task(task_id)
    if not task:
        return {"status": "failed", "progress": 0, "result": None}
    return {
        "status": task["status"],
        "progress": task["progress"],
        "result": task["result"]
    }


UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload_rar/")
async def upload_rar(file: UploadFile = File(...)):
    # Сохраняем архив во временную папку
    file_location = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Путь к rar2john
    rar2john_path = "/opt/homebrew/Cellar/john-jumbo/1.9.0_1/share/john/rar2john"
    # Путь к john
    john_path = "/opt/homebrew/bin/john"

    # Извлекаем хеш из архива
    try:
        result = subprocess.run(
            [rar2john_path, file_location],
            capture_output=True,
            text=True,
            check=True
        )
        hash_data = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to extract hash: {e.stderr}"}

    # Сохраняем хеш во временный файл
    hash_file = file_location + ".hash"
    with open(hash_file, "w") as f:
        f.write(hash_data)

    # Запускаем подбор пароля через john
    try:
        subprocess.run(
            [john_path, hash_file],
            check=True
        )
    except subprocess.CalledProcessError as e:
        return {"error": f"John failed: {e.stderr}"}

    # Получаем результат
    try:
        result = subprocess.run(
            [john_path, "--show", hash_file],
            capture_output=True,
            text=True,
            check=True
        )
        password_info = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to get password: {e.stderr}"}
    try:
        result = subprocess.run(
            [john_path, "--show", hash_file],
            capture_output=True,
            text=True,
            check=True
        )
        password_info = result.stdout.strip()
    
        # Извлечь только пароль
        lines = password_info.strip().splitlines()
        if lines and ":" in lines[0]:
            cracked_password = lines[0].split(":")[1]
        else:
            cracked_password = None

    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to get password: {e.stderr}"}

    return {
        "message": "Password cracked!",
        "details": password_info,
        "password": cracked_password
    }