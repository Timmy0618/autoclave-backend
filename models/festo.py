from models.shared import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime


class FestoMain(db.Model):
    __tablename__ = 'festo_main'
    id = Column(Integer, primary_key=True)
    formula_main_id = Column(Integer, ForeignKey('formula_main.id'))
    name = Column(String(length=50))
    slave_id = Column(Integer)
    batch_number = Column(String(length=50), unique=True)
    warning_time = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    festo_current_detail = relationship(
        'FestoCurrentDetail', uselist=False, back_populates='festo_main')
    schedule = relationship('Schedule', uselist=False,
                            back_populates='festo_main')
    formula = relationship('FormulaMain', back_populates='festos')


class FestoCurrentDetail(db.Model):
    __tablename__ = 'festo_current_detail'
    id = Column(Integer, primary_key=True)
    slave_id = Column(Integer, unique=True)
    pressure = Column(Float)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    festo_main_id = Column(Integer, ForeignKey('festo_main.id'))
    festo_main = relationship(
        'FestoMain', back_populates='festo_current_detail')


class FestoHistory(db.Model):
    __tablename__ = 'festo_history'
    id = Column(Integer, primary_key=True)
    slave_id = Column(Integer)
    batch_number = Column(String(length=50))
    formula_name = Column(String(length=50))
    sequence = Column(Integer)
    pressure = Column(Float)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
