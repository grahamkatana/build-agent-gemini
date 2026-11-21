import re
import time
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from src.connectors.gemini import get_gemini_response
from src.schemas.chat import ApiMeta, ChatData, ChatResponse, RouteReference

# Matches route codes like CENTURION, BROOKLYN_8, PRETORIA_NORTH_1, ROUTE_7
ROUTE_CODE_PATTERN = re.compile(r"\b([A-Z]{3,}(?:_[A-Z0-9]+)*)\b")
KNOWN_NON_ROUTES = {"CBD", "UTC", "SQL", "API", "JSON", "SAML", "SSO", "HTTP", "HTTPS"}


def _extract_route_references(text: str) -> list[RouteReference]:
    seen: set[str] = set()
    refs: list[RouteReference] = []
    for match in ROUTE_CODE_PATTERN.findall(text):
        if match not in KNOWN_NON_ROUTES and match not in seen:
            seen.add(match)
            refs.append(RouteReference(route_code=match))
    return refs


def handle_bus_chat(query: str, session_id: str | None = None) -> ChatResponse:
    cleaned_query = query.strip()
    if not cleaned_query:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Query must not be empty.",
        )

    start = time.perf_counter()
    try:
        raw_answer = get_gemini_response(cleaned_query)
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
            routes_mentioned=_extract_route_references(raw_answer),
        ),
        meta=ApiMeta(
            session_id=session_id,
            latency_ms=elapsed_ms,
        ),
    )
