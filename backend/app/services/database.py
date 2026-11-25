import logging
import sqlite3
import json
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

# Try SQLAlchemy if available, otherwise use Python's built-in sqlite3
try:
    from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
    from sqlalchemy.orm import declarative_base, sessionmaker
    
    Base = declarative_base()

    class CandidateRecord(Base):
        __tablename__ = "candidates"
        id = Column(String, primary_key=True, index=True)
        full_name = Column(String, nullable=False)
        email = Column(String, nullable=True)
        years_experience = Column(Float, default=0.0)
        skills_json = Column(Text, default="[]")
        created_at = Column(DateTime, default=datetime.utcnow)

    class EvaluationRecord(Base):
        __tablename__ = "evaluations"
        id = Column(String, primary_key=True, index=True)
        candidate_id = Column(String, index=True, nullable=False)
        job_id = Column(String, index=True, nullable=False)
        overall_score = Column(Float, default=0.0)
        recommendation = Column(String, nullable=False)
        scorecard_json = Column(Text, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow)

    engine = create_engine(
        settings.DATABASE_URL, 
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    HAS_SQLALCHEMY = True

    def init_db():
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized via SQLAlchemy.")

except ImportError:
    HAS_SQLALCHEMY = False
    DB_FILE = "recruiting_copilot.db"

    class MockRecord:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    CandidateRecord = MockRecord
    EvaluationRecord = MockRecord

    class SqliteSession:
        def __init__(self):
            self.conn = sqlite3.connect(DB_FILE)
            self._init_tables()

        def _init_tables(self):
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id TEXT PRIMARY KEY,
                    full_name TEXT,
                    email TEXT,
                    years_experience REAL,
                    skills_json TEXT,
                    created_at TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evaluations (
                    id TEXT PRIMARY KEY,
                    candidate_id TEXT,
                    job_id TEXT,
                    overall_score REAL,
                    recommendation TEXT,
                    scorecard_json TEXT,
                    created_at TEXT
                )
            """)
            self.conn.commit()

        def add(self, obj):
            cursor = self.conn.cursor()
            if hasattr(obj, "full_name"):
                cursor.execute(
                    "INSERT OR REPLACE INTO candidates VALUES (?, ?, ?, ?, ?, ?)",
                    (obj.id, obj.full_name, getattr(obj, "email", ""), obj.years_experience, getattr(obj, "skills_json", "[]"), str(datetime.utcnow()))
                )
            elif hasattr(obj, "scorecard_json"):
                cursor.execute(
                    "INSERT OR REPLACE INTO evaluations VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (obj.id, obj.candidate_id, obj.job_id, obj.overall_score, obj.recommendation, obj.scorecard_json, str(datetime.utcnow()))
                )

        def commit(self):
            self.conn.commit()

        def close(self):
            self.conn.close()

    def SessionLocal():
        return SqliteSession()

    def init_db():
        s = SqliteSession()
        s.close()
        logger.info("Database initialized via Python standard library sqlite3.")
