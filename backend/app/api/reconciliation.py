from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboard import ReconciliationRunCreate, ReconciliationRunResponse, ReconciliationResultsResponse
from app.reconciliation.engine import ReconciliationEngine

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])


@router.post("/run", response_model=dict)
def run_reconciliation(
    run_data: ReconciliationRunCreate,
    db: Session = Depends(get_db)
):
    """Run reconciliation for a period."""
    engine = ReconciliationEngine(db)
    return engine.run_reconciliation(
        period_start=run_data.period_start,
        period_end=run_data.period_end,
        user="api_user"
    )


@router.get("/runs", response_model=list[ReconciliationRunResponse])
def get_reconciliation_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of reconciliation runs."""
    from app.repositories.reconciliation_run import ReconciliationRunRepository
    repo = ReconciliationRunRepository(db)
    runs, _ = repo.get_list(page=page, page_size=page_size)
    return [ReconciliationRunResponse.model_validate(r) for r in runs]


@router.get("/runs/{run_id}", response_model=ReconciliationRunResponse)
def get_reconciliation_run(
    run_id: int,
    db: Session = Depends(get_db)
):
    """Get a reconciliation run by ID."""
    from app.repositories.reconciliation_run import ReconciliationRunRepository
    repo = ReconciliationRunRepository(db)
    run = repo.get_by_id(run_id)
    if not run:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Reconciliation run not found")
    return ReconciliationRunResponse.model_validate(run)


@router.get("/runs/{run_id}/results", response_model=ReconciliationResultsResponse)
def get_reconciliation_results(
    run_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    match_result: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get results from a reconciliation run."""
    engine = ReconciliationEngine(db)
    items, total = engine.get_reconciliation_results(
        run_id=run_id,
        page=page,
        page_size=page_size,
        match_result=match_result
    )
    return ReconciliationResultsResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )
