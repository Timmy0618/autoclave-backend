from models.shared import db
from sqlalchemy import Column, Integer, Boolean, DateTime
from datetime import datetime


class Pid(db.Model):
    __tablename__ = 'pid'
    id = Column(Integer, primary_key=True)
    kp = Column(Integer)
    ki = Column(Integer)
    kd = Column(Integer)
    step = Column(Integer)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
