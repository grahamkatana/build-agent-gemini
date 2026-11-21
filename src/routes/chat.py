from fastapi import APIRouter, Request

from src.core.limiter import limiter
from src.consumption.handlers.bus_chat_handler import handle_bus_chat
from src.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit("15/minute")
def query_bus_assistant(request: Request, payload: ChatRequest) -> ChatResponse:
    return handle_bus_chat(
        query=payload.query,
        session_id=payload.session_id,
        include_map_data=payload.include_map_data,
    )
