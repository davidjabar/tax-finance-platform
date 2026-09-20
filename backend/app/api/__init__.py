from fastapi import APIRouter
from .transactions import router as transactions_router
from .vendors import router as vendors_router
from .tax_transactions import router as tax_transactions_router
from .dashboard import router as dashboard_router
from .reconciliation import router as reconciliation_router
from .exceptions import router as exceptions_router
from .analytics import router as analytics_router
from .ingestion import router as ingestion_router

api_router = APIRouter()

api_router.include_router(dashboard_router)
api_router.include_router(transactions_router)
api_router.include_router(vendors_router)
api_router.include_router(tax_transactions_router)
api_router.include_router(reconciliation_router)
api_router.include_router(exceptions_router)
api_router.include_router(analytics_router)
api_router.include_router(ingestion_router)
