"""
    author: Jin-Mo,Lin
    email: s106003041@g.ksu.edu.tw
    description: MySQL Database
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///AI_Result.db')

Base = declarative_base()


def create_session():
    Session = sessionmaker(engine)
    session = Session()
    return session


def create_table():
    if not os.path.isfile('AI_Result.db'):
        AIResult.__table__.create(engine)


def drop_table():
    AIResult.__table__.drop(engine)


class AIResult(Base):
    __tablename__ = 'ai_result'
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    model_use_id = Column(String, nullable=False)
    model_version = Column(String, nullable=False)
    kde = Column(Float)
    mse = Column(Float)
    decibel = Column(Float)     # dBFS
    ai_score1 = Column(Integer)
    ai_score2 = Column(Integer)
    freq_result = Column(String, nullable=False)
    ai_result = Column(String, nullable=False)
    final_result = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


if __name__ == '__main__':
    session = create_session()
    AIResult.__table__.create(engine)

# ==============================================================================
# ------------------------------------ END -------------------------------------
# ==============================================================================
