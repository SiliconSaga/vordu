from sqlalchemy import create_engine, Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./vordu.db"

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
