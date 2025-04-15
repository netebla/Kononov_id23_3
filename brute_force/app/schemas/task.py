from pydantic import BaseModel
from typing import Optional

# Схема запроса для старта брутфорс-задачи
class BruteforceRequest(BaseModel):
    hash: str
    charset: str
    max_length: int
    mode: str 

# Схема ответа на создание задачи
class TaskCreateResponse(BaseModel):
    task_id: str

# Схема для ответа о статусе задачи
class TaskStatusResponse(BaseModel):
    status: str  # running / completed / failed
    progress: int  # Процент выполнения
    result: Optional[str] = None  # Найденный пароль или None