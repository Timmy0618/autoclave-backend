from models.shared import db
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class ScheduleDetail(db.Model):
    __tablename__ = 'schedule_detail'
    id = Column(Integer, primary_key=True)
    pressure = Column(Integer)
    process_time = Column(Integer)
    reset_times = Column(Integer, default=0)
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    schedules = relationship('Schedule', backref='schedule_detail')


class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    festo_main_id = Column(Integer, ForeignKey('festo_main.id'))
    schedule_detail_id = Column(Integer, ForeignKey('schedule_detail.id'))
    sequence = Column(Integer)
    check_pressure = Column(Boolean, default=False)
    status = Column(Integer)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    festo_main = relationship('FestoMain', back_populates='schedules')
