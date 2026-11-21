import re
import time
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from src.connectors.gemini import get_gemini_response
from src.schemas.chat import ApiMeta, ChatData, ChatResponse
from src.services.map_service import fetch_routes_and_map_data

ROUTE_CODE_PATTERN = re.compile(r"\b([A-Z]{3,}(?:_[A-Z0-9]+)*)\b")
KNOWN_NON_ROUTES = {"CBD", "UTC", "SQL", "API", "JSON", "SAML", "SSO", "HTTP", "HTTPS"}


def _extract_candidate_codes(text: str) -> list[str]:
    seen: set[str] = set()
    codes: list[str] = []
    for match in ROUTE_CODE_PATTERN.findall(text):
        if match not in KNOWN_NON_ROUTES and match not in seen:
            seen.add(match)
            codes.append(match)
    return codes


def handle_bus_chat(
    query: str,
    session_id: str | None = None,
    include_map_data: bool = True,
) -> ChatResponse:
    cleaned_query = query.strip()
    if not cleaned_query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Query must not be empty.",
        )

    start = time.perf_counter()
    try:
        raw_answer = get_gemini_response(cleaned_query)
        candidate_codes = _extract_candidate_codes(raw_answer)
        route_refs, map_routes = fetch_routes_and_map_data(
            candidate_codes, include_map_data=include_map_data
        )
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transit database is temporarily unavailable.",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Upstream AI service error: {exc}",
        ) from exc

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return ChatResponse(
        status="success",
        data=ChatData(
            answer=raw_answer,
            routes_mentioned=route_refs,
            map_routes=map_routes,
        ),
        meta=ApiMeta(
            session_id=session_id,
            latency_ms=elapsed_ms,
        ),
    )
