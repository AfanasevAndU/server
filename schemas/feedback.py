from pydantic import BaseModel
from datetime import datetime

class Feedback(BaseModel):
    company = str
    author = str
    text = str
    rate = str
    date = datetime

class FeedbackCreate(Feedback):
    pass

class Feedback(Feedback):
    id: int

    class Config:
        orm_mode = True