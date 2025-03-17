from sqlalchemy import Column, Integer, Float, String, DateTime
from database import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String)
    author = Column(String)
    text = Column(String)
    rate = Column(String)
    date = Column(DateTime)