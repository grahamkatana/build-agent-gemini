from typing import Any, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="User question about Tshwane Bus routes, stops, or timetables.",
        examples=["What time does the first weekday bus leave for Centurion?"],
    )
    session_id: str | None = Field(
        default=None,
        max_length=64,
        description="Optional client-side conversation correlation ID.",
    )


class RouteReference(BaseModel):
    route_code: str
    name: str | None = None
    region: str | None = None


class ChatData(BaseModel):
    answer: str = Field(..., description="Formatted markdown/text answer for display.")
    routes_mentioned: list[RouteReference] = Field(default_factory=list)
    model_used: str = Field(default="gemini-3.5-flash-lite")


class ApiMeta(BaseModel):
    session_id: str | None = None
    latency_ms: int


class ChatResponse(BaseModel):
    status: Literal["success", "blocked", "error"] = "success"
    data: ChatData
    meta: ApiMeta
