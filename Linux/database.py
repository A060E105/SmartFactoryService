"""
    author: Jin-Mo,Lin
    email: s106003041@g.ksu.edu.tw
    description: MySQL Database
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///AI_Result.db')

Base = declarative_base()


def create_session():
    Session = sessionmaker(engine)
    session = Session()
    return session


class AIResult(Base):
    __tablename__ = 'ai_result'
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    kde = Column(Float)
    mse = Column(Float)
    result = Column(String, nullable=False)
    create_at = Column(DateTime(timezone=True), server_default=func.now())


if __name__ == '__main__':
    session = create_session()
    AIResult.__table__.create(engine)

# ==============================================================================
# ------------------------------------ END -------------------------------------
# ==============================================================================
