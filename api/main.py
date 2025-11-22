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
    scenarios_total: int
    scenarios_passed: int
    steps_total: int
    steps_passed: int

class MatrixResponse(BaseModel):
    project: str
    row: str
    phase: int
    status: str
    completion: int
    scenarios_total: int
    scenarios_passed: int
    steps_total: int
    steps_passed: int

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
                completion=item.completion,
                scenarios_total=item.scenarios_total,
                scenarios_passed=item.scenarios_passed,
                steps_total=item.steps_total,
                steps_passed=item.steps_passed
            )
            db.add(cell)
        else:
            cell.status = item.status
            cell.completion = item.completion
            cell.scenarios_total = item.scenarios_total
            cell.scenarios_passed = item.scenarios_passed
            cell.steps_total = item.steps_total
            cell.steps_passed = item.steps_passed
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
            completion=c.completion,
            scenarios_total=c.scenarios_total,
            scenarios_passed=c.scenarios_passed,
            steps_total=c.steps_total,
            steps_passed=c.steps_passed
        ) for c in cells
    ]
