# Tshwane Bus Services AI Assistant API

An AI-powered transit assistant and geospatial route API for **Tshwane Bus Services (TBS)** in Pretoria/Tshwane, South Africa. Built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **Google Gemini** (function/tool calling), and **SlowAPI**, it answers natural-language timetable and stop queries while returning RFC 7946 **GeoJSON** route paths and stop markers for frontend mapping platforms.

> **Note on Map Data:** Map hydration (`map_routes`) currently executes synchronously against PostgreSQL without a dedicated map-query timeout; ensure database connection pooling and query timeouts are configured appropriately for production traffic.

---

## System Architecture

```mermaid
flowchart TD
    Client["Frontend Client / Map UI<br/>(React / Mapbox / Leaflet)"]
    
    subgraph FastAPI ["FastAPI Application (src/app.py)"]
        Middleware["CORS & SlowAPI Rate Limiter<br/>(60/min global, 15/min /chat)"]
        HealthRoute["GET /api/v1/health<br/>(src/routes/health.py)"]
        ChatRoute["POST /api/v1/chat<br/>(src/routes/chat.py)"]
        Handler["Bus Chat Handler<br/>(src/consumption/handlers/bus_chat_handler.py)"]
        MapService["GeoJSON Map Service<br/>(src/services/map_service.py)"]
    end

    subgraph AI ["AI & Tool Execution Layer"]
        Gemini["Gemini Connector<br/>(src/connectors/gemini.py)"]
        LLM["Google Gemini API<br/>(Tool / Function Calling)"]
    end

    subgraph Storage ["Data Layer"]
        DB[("PostgreSQL<br/>(routes, route_variants,<br/>stops, timetable_entries)")]
        Seed["SQL Seed & Loader<br/>(src/database/combined.sql<br/>src/scripts/load_data.py)"]
    end

    Client -->|"HTTP / JSON"| Middleware
    Middleware --> HealthRoute
    Middleware --> ChatRoute
    HealthRoute -->|"SELECT 1"| DB
    ChatRoute --> Handler
    Handler -->|"1. Natural Language Query"| Gemini
    Gemini <-->|"2. Tool Calls & Grounded Answer"| LLM
    Gemini <-->|"3. SQL Transit Lookups"| DB
    Handler -->|"4. Extract Route Codes & Hydrate GeoJSON"| MapService
    MapService -->|"5. Fetch Ordered Stops & Coordinates"| DB
    Handler -->|"6. ChatResponse (Markdown + GeoJSON)"| Client
    Seed -.->|"Initial Data Load"| DB