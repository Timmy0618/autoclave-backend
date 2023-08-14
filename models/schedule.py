from models.shared import db
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    festo_main_id = Column(Integer, ForeignKey('festo_main.id'))
    pid_id = Column(Integer, ForeignKey('pid.id'))
    check_pressure = Column(Boolean, default=False)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    festo_main = relationship('FestoMain', back_populates='schedules')
    pid = relationship('Pid', back_populates='schedules')
    # Updated back_populates value
    schedule_details = relationship(
        'ScheduleDetail', back_populates='schedule')


class ScheduleDetail(db.Model):
    __tablename__ = 'schedule_detail'
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('schedule.id'))
    sequence = Column(Integer)
    pressure = Column(Integer)
    status = Column(Integer)
    process_time = Column(Integer)
    reset_times = Column(Integer, default=0)
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Updated back_populates value
    schedule = relationship('Schedule', back_populates='schedule_details')
