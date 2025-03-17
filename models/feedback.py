from sqlalchemy import Column, Integer, Float, String, DateTime
from db import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    message = Column(String)
    site = Column(String)
    stars = Column(Float)
    date = Column(DateTime)