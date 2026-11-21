from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.database.db import engine

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get("")
def list_main_routes() -> list[dict]:
    sql = text("""
        SELECT
            route_code,
            name,
            area,
            region,
            terminus_from,
            terminus_to,
            wd_service,
            sat_service,
            has_start_loop
        FROM routes
        ORDER BY region NULLS LAST, name ASC
    """)
    try:
        with engine.connect() as conn:
            rows = conn.execute(sql).mappings().all()
        return [dict(r) for r in rows]
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to load transit routes.",
        ) from exc
