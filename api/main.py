from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Base, engine, MatrixCell, get_db
from pydantic import BaseModel
from typing import List, Optional

from fastapi.middleware.cors import CORSMiddleware

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vörðu API", description="The Living Roadmap Aggregator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class IngestItem(BaseModel):
    project_name: str
    row_id: str
    phase_id: int
    status: str  # "pass", "fail", "pending"
    completion: int

class MatrixResponse(BaseModel):
    project: str
    row: str
    phase: int
    status: str
    completion: int

@app.get("/")
def read_root():
    return {"message": "Vörðu API is running. The Cairn stands tall."}

@app.post("/ingest")
def ingest_status(items: List[IngestItem], db: Session = Depends(get_db)):
    # Bulk upsert logic
    updated_count = 0
    for item in items:
        cell = db.query(MatrixCell).filter(
            MatrixCell.project_name == item.project_name,
            MatrixCell.row_id == item.row_id,
            MatrixCell.phase_id == item.phase_id
        ).first()

        if not cell:
            cell = MatrixCell(
                project_name=item.project_name,
                row_id=item.row_id,
                phase_id=item.phase_id,
                status=item.status,
                completion=item.completion
            )
            db.add(cell)
        else:
            cell.status = item.status
            cell.completion = item.completion
        updated_count += 1
    
    db.commit()
    return {"status": "updated", "count": updated_count}

@app.get("/matrix", response_model=List[MatrixResponse])
def get_matrix(db: Session = Depends(get_db)):
    cells = db.query(MatrixCell).all()
    return [
        MatrixResponse(
            project=c.project_name,
            row=c.row_id,
            phase=c.phase_id,
            status=c.status,
            completion=c.completion
        ) for c in cells
    ]
