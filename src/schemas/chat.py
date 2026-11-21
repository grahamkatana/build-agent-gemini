from typing import Any, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="User question about Tshwane Bus routes, stops, or timetables.",
        examples=["Show me the route and stops for Centurion"],
    )
    session_id: str | None = Field(
        default=None,
        max_length=64,
        description="Optional client-side conversation correlation ID.",
    )
    include_map_data: bool = Field(
        default=True,
        description="When true, attaches GeoJSON route paths and stop markers for mentioned routes.",
    )


class RouteReference(BaseModel):
    route_code: str
    name: str | None = None
    region: str | None = None
    terminus_from: str | None = None
    terminus_to: str | None = None


class GeoJsonFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: dict[str, Any]
    properties: dict[str, Any]


class RouteMapData(BaseModel):
    route_code: str
    name: str
    region: str | None = None
    bbox: list[float] | None = Field(
        default=None,
        description="[min_lon, min_lat, max_lon, max_lat] for auto-fitting the map viewport.",
    )
    geojson: dict[str, Any] = Field(
        ...,
        description="RFC 7946 FeatureCollection containing LineString paths and Point stops.",
    )


class ChatData(BaseModel):
    answer: str = Field(..., description="Formatted markdown/text answer for display.")
    routes_mentioned: list[RouteReference] = Field(default_factory=list)
    map_routes: list[RouteMapData] = Field(
        default_factory=list,
        description="GeoJSON FeatureCollections for every route referenced in the answer.",
    )
    model_used: str = Field(default="gemini-3.5-flash-lite")


class ApiMeta(BaseModel):
    session_id: str | None = None
    latency_ms: int


class ChatResponse(BaseModel):
    status: Literal["success", "blocked", "error"] = "success"
    data: ChatData
    meta: ApiMeta
