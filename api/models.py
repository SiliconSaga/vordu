from sqlalchemy import create_engine, Column, Integer, String
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

class System(Base):
    __tablename__ = "systems"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    label = Column(String)
    description = Column(String)
    domain = Column(String)

class Row(Base):
    __tablename__ = "rows"
    
    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String, index=True) # Foreign key to System.name logical
    key = Column(String) # The component name/ID
    label = Column(String)
    parent_row = Column(String, nullable=True) # For sub-components

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
