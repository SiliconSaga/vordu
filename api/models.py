from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# Allow overriding DB URL via env var (e.g. for K8s persistence)
# Default to local file if not set
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vordu.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class MatrixCell(Base):
    __tablename__ = "matrix_cells"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, index=True)
    row_id = Column(String) # The capability ID (e.g., "identity")
    phase_id = Column(Integer) # 0, 1, 2, 3
    status = Column(String) # "pass", "fail", "pending"
    completion = Column(Integer, default=0) # 0-100
    
    # Granular Metrics
    scenarios_total = Column(Integer, default=0)
    scenarios_passed = Column(Integer, default=0)
    steps_total = Column(Integer, default=0)
    steps_passed = Column(Integer, default=0)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
