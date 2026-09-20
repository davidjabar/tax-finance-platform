from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.exception import ExceptionRepository
from app.schemas.common import ExceptionListResponse, ExceptionResponse, ExceptionUpdate
from app.models.exception import ExceptionStatus


class ExceptionService:
    def __init__(self, db: Session):
        self.db = db
        self.exception_repo = ExceptionRepository(db)

    def get_exceptions(
        self,
        page: int = 1,
        page_size: int = 50,
        exception_type: Optional[str] = None,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        assigned_user: Optional[str] = None,
        search: Optional[str] = None
    ) -> ExceptionListResponse:
        exceptions, total = self.exception_repo.get_list(
            page=page,
            page_size=page_size,
            exception_type=exception_type,
            status=status,
            severity=severity,
            assigned_user=assigned_user,
            search=search
        )

        items = [ExceptionResponse.model_validate(e) for e in exceptions]
        total_pages = (total + page_size - 1) // page_size

        return ExceptionListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def get_exception(self, exception_id: int) -> Optional[ExceptionResponse]:
        exception = self.exception_repo.get_by_id(exception_id)
        if not exception:
            return None
        return ExceptionResponse.model_validate(exception)

    def update_exception(
        self,
        exception_id: int,
        update_data: ExceptionUpdate,
        user: str = "system"
    ) -> Optional[ExceptionResponse]:
        data = update_data.model_dump(exclude_unset=True)
        if not data:
            return self.get_exception(exception_id)

        exception = self.exception_repo.update(exception_id, data, user)
        if not exception:
            return None
        return ExceptionResponse.model_validate(exception)

    def get_summary_stats(self):
        return self.exception_repo.get_summary_stats()
