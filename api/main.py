from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .models import Base, engine, MatrixCell, get_db
from pydantic import BaseModel
from typing import List, Optional

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Vörðu API", description="The Living Roadmap Aggregator")

# Mount static files (after building UI)
# Ensure the directory exists to avoid errors during dev if not built
if os.path.exists("ui/dist"):
    app.mount("/assets", StaticFiles(directory="ui/dist/assets"), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://vordu.siliconsaga.org"],
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



@app.get("/health")
def health_check():
    return {"message": "Vörðu API is running. The Cairn stands tall."}

from fastapi.security import APIKeyHeader
from fastapi import Security

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    expected_key = os.getenv("VORDU_API_KEY")
    if not expected_key:
        # If no key configured in env, allow open access (dev mode). Otherwise expect key present in environment.
        return None
        
    if api_key_header == expected_key:
        return api_key_header
    raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.post("/ingest")
def ingest_status(items: List[IngestItem], db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
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

# Serve React App (SPA)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # Allow API routes to pass through if they weren't caught above
    if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Check if the file exists in the UI build directory (e.g. logo.png, favicon.ico)
    file_path = os.path.join("ui/dist", full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Fallback to index.html for SPA routing
    if os.path.exists("ui/dist/index.html"):
        return FileResponse("ui/dist/index.html")
    return {"message": "UI not built. Run 'npm run build' in ui/ directory."}
