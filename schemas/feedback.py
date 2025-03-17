from pydantic import BaseModel
from datetime import datetime

# Базовый класс для отзыва
class FeedbackBase(BaseModel):
    company: str
    author: str
    text: str
    rate: str
    date: datetime

# Класс для создания отзыва
class FeedbackCreate(FeedbackBase):
    pass

# Класс для отзыва с ID
class Feedback(FeedbackBase):
    id: int

    class Config:
        orm_mode = True  # Для работы с SQLAlchemy
