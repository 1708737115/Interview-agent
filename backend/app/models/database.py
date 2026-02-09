from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()

# Create engine
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="processing")  # processing, completed, failed
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    
    id = Column(String, primary_key=True)
    mode = Column(String, nullable=False)  # structured, open
    status = Column(String, default="active")  # active, paused, completed
    candidate_info = Column(Text, nullable=True)
    knowledge_base_ids = Column(JSON, default=list)
    current_question_index = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=30)
    started_at = Column(DateTime, default=datetime.now)
    ended_at = Column(DateTime, nullable=True)


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)
    difficulty = Column(Integer, default=3)
    context = Column(Text, nullable=True)
    expected_points = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.now)


class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    question_id = Column(String, nullable=False)
    answer_text = Column(Text, nullable=False)
    evaluation = Column(JSON, default=dict)  # 存储评估结果
    total_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
