from models.shared import db
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


class FormulaMain(db.Model):
    __tablename__ = 'formula_main'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    formula_details = relationship('FormulaDetail', backref='formula_main')


class FormulaDetail(db.Model):
    __tablename__ = 'formula_detail'
    id = Column(Integer, primary_key=True)
    formula_main_id = Column(Integer, ForeignKey('formula_main.id'))
    sequence = Column(Integer)
    pressure = Column(Integer)
    process_time = Column(Integer)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
