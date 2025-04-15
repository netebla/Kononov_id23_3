from fastapi import FastAPI
from app.api.routes import router
from app.db.database import Base, engine

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Инициализация приложения
app = FastAPI()

# Подключаем роуты
app.include_router(router)