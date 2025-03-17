from pydantic import BaseModel
from datetime import datetime

class Feedback(BaseModel):
    name: str
    message: str
    site: str
    stars: float
    date: datetime

class TaskCreate(Feedback):
    pass

class Task(Feedback):
    id: int

    class Config:
        orm_mode = True