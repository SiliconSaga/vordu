from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Base, engine, MatrixCell, get_db
from pydantic import BaseModel
from typing import List, Optional

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vörðu API", description="The Living Roadmap Aggregator")

# Pydantic Models
class IngestItem(BaseModel):
    project_name: str
    row_id: str
    phase_id: int
    status: str  # "pass", "fail", "pending"

class MatrixResponse(BaseModel):
    project: str
    row: str
    phase: int
    status: str

@app.get("/")
def read_root():
    return {"message": "Vörðu API is running. The Cairn stands tall."}

@app.post("/ingest")
def ingest_status(item: IngestItem, db: Session = Depends(get_db)):
    # Simple upsert logic for now
    # In a real scenario, we might track history. Here we just update the current state.
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
            status=item.status
        )
        db.add(cell)
    else:
        cell.status = item.status
    
    db.commit()
    return {"status": "updated", "cell": f"{item.project_name}::{item.row_id}::{item.phase_id}"}

@app.get("/matrix", response_model=List[MatrixResponse])
def get_matrix(db: Session = Depends(get_db)):
    cells = db.query(MatrixCell).all()
    return [
        MatrixResponse(
            project=c.project_name,
            row=c.row_id,
            phase=c.phase_id,
            status=c.status
        ) for c in cells
    ]
