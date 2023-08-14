from models.shared import db
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=50), unique=True)
    password = Column(String(length=50))
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
