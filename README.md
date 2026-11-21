# TBS AI Agent — Centralized Tshwane Bus Service & Gemini Transit Assistant

> **Turning fragmented municipal PDF timetables into a conversational, map-aware transit experience for Tshwane commuters.**

---

## 1. Executive Summary & Business Case

### The Problem: PDF Fragmentation on the Official Portal
Currently, commuters looking for Tshwane Bus Services (TBS) schedules via the official municipal portal ([tshwane.gov.za/?page_id=723](https://www.tshwane.gov.za/?page_id=723)) must browse static links and download individual PDF files for each route. This creates significant friction:

- **High Commuter Effort**: Users must know which corridor or suburb PDF to download, open multiple documents to compare connections, and manually scan dense timetable tables.
- **Poor Mobile Usability**: Pinch-zooming multi-page PDFs on smartphones while rushing for a bus leads to missed departures and frustration.
- **No Natural-Language Discovery**: A commuter cannot simply ask *"When is the first weekday bus to Centurion?"* or *"Which routes connect Pretoria CBD to Hatfield?"*
- **Zero Spatial Context**: Static PDFs list street names without showing where stops sit on a map, how outbound and inbound paths differ, or how a journey progresses stop-by-stop.

### The Opportunity: Centralize + Gemini AI Agent
By consolidating all TBS route metadata, stop coordinates, and weekday/Saturday timetables into a single structured backend and pairing it with a **Gemini AI Agent**, TBS AI Agent transforms static municipal documents into an instant, conversational transit assistant.

### Business Value & Impact

| Stakeholder | Current Pain (PDFs) | Value Delivered by TBS AI Agent |
| :--- | :--- | :--- |
| **Daily Commuters** | Tedious PDF downloads, hard to read on mobile, no quick transfer lookup | Natural-language Q&A in seconds, extracted departure times, interactive route maps, and stop-by-stop simulation |
| **Occasional Riders & Visitors** | Unfamiliar with route codes or Pretoria suburb corridors | Ask by landmark or destination (*"Brooklyn"*, *"Pretoria North"*, *"Centurion"*) without knowing route numbers |
| **Municipal Transit Operations** | Manual PDF upkeep, high call-center/support queries for basic times | Single centralized source of truth, reduced commuter support load, and query analytics revealing high-demand corridors |
| **Accessibility & Inclusion** | Screen-reader unfriendly scanned/table PDFs | Clean semantic HTML prose, structured tables, high-contrast UI, and conversational guidance |

---

## 2. How the System Works

```
  Official TBS Route PDFs (tshwane.gov.za/?page_id=723)
                        │
                        ▼  Centralized Ingestion & Structuring
        ┌───────────────────────────────┐
        │   TBS Transit Knowledge Base  │
        │  • Corridors & regions        │
        │  • Weekday / Saturday times   │
        │  • GeoJSON stops & terminals  │
        └───────────────┬───────────────┘
                        │
                        ▼  Grounded Retrieval + Reasoning
        ┌───────────────────────────────┐
        │       Gemini AI Agent         │
        │  Understands natural language │
        │  & returns answers + GeoJSON  │
        └───────────────┬───────────────┘
                        │
                        ▼  REST API (/api/v1/*)
        ┌───────────────────────────────┐
        │    TBS AI Agent Web App       │
        │  Chat-first UI + Map & Sim    │
        └───────────────────────────────┘
```

---

## 3. UI & Product Architecture (Learned from the Interface)

The interface is intentionally designed as a **chat-first agentic workspace**—putting conversational assistance at the center while keeping corridor browsing, mapping, and live journey simulation one click away.

### 1. Center Stage: Agentic Chat Workspace
- **Conversational Entry Point**: Welcomes users with plain-language prompt starters (*"First weekday bus to Centurion?"*, *"Show route and stops for Brooklyn"*, *"Saturday buses for Pretoria North"*, *"Which routes connect Pretoria CBD to Hatfield?"*).
- **Session Memory**: Maintains continuity across follow-up questions via `sessionStorage` (`tbs_session_id`).
- **Rich Markdown Responses**: Renders formatted timetables, bullet lists, and route notes cleanly alongside response latency indicators.
- **Embedded Trip Artifact Cards**: When the agent identifies a corridor, it attaches a structured summary card directly inside the reply containing:
  - Route name, `route_code`, and region
  - Automatically extracted departure times (`HH:MM`)
  - Origin-to-terminus spine showing outbound and inbound stop counts
  - One-click **View on Map** and **Simulate Journey** actions

### 2. Left Rail: Searchable Corridor Explorer
- **Live Text Filter**: Instant client-side filtering across route names, route codes, regions, and suburbs.
- **Region Tabs**: Dynamic region chips (populated from `/api/v1/routes`) to narrow down corridors across Tshwane.
- **Service Indicators**: Displays Weekday and Saturday service availability per corridor; clicking any corridor immediately prompts the agent for a full route overview, stops, and schedule.
- **Live Connectivity Footer**: Polls `/api/v1/health` to surface real-time `Online` / `Offline` status alongside the total number of indexed corridors.

### 3. Supporting Right Drawer: Route Map & Live Journey Simulator
Rather than letting the map overwhelm the conversation, spatial tools live in a collapsible side drawer (and full-screen view on mobile) with two modes:

- **Route Map (Leaflet + OpenStreetMap)**:
  - Keyless OpenStreetMap tiles styled for crisp street legibility.
  - Color-coded directional geometry: **Outbound** (solid blue), **Inbound** (dashed green), **Terminals** (dark slate markers), and **CBD points** (amber markers) with street/stop popups.
  - Auto-fits bounds to the active corridor's stops or bounding box.
- **Live Journey Simulator**:
  - Switch between any loaded route and toggle **Outbound** or **Inbound** direction.
  - Adjustable playback speeds (**1×**, **2×**, **5×**) with Play/Pause and a live progress bar.
  - Smooth `requestAnimationFrame` bus marker interpolation along the polyline with an active progress trail.
  - Interactive stop-by-stop timeline showing passed/current stops, estimated minutes ahead, and click-to-jump navigation.

---

## 4. API Integration Contract

The frontend connects to an existing backend through three REST endpoints:

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/api/v1/health` | `GET` | Verifies API availability for the sidebar connection indicator (`Online` / `Offline`). |
| `/api/v1/routes` | `GET` | Returns the centralized corridor catalog (`route_code`, `name`, `region`, `area`, `wd_service`, `sat_service`) used to populate the corridor explorer and simulator selector. |
| `/api/v1/chat` | `POST` | Accepts `{ query, session_id, include_map_data: true }` and returns the Gemini agent response (`data.answer`), structured `data.routes_mentioned` (`terminus_from`, `terminus_to`, `route_code`, `region`), `data.map_routes` (GeoJSON stops with `direction`, `sequence_no`, `stop_type`, `street`, and `bbox`), and `meta.latency_ms`. |

---

## 5. Strategic Next Steps & Expansion Roadmap

1. **Automated PDF Sync Pipeline**: Scheduled scraper/parser watching [tshwane.gov.za/?page_id=723](https://www.tshwane.gov.za/?page_id=723) so timetable revisions automatically update the centralized knowledge base.
2. **Multilingual Commuter Support**: Leverage Gemini's native multilingual capabilities to answer commuter queries in Sepedi, Afrikaans, isiZulu, Setswana, and English.
3. **Multi-Modal Transfers**: Extend corridor grounding to connect TBS routes with A Re Yeng BRT, Gautrain stations, and Metrorail hubs.
4. **Live Fleet Telemetry (GTFS-RT)**: Replace simulated bus movement with real-time GPS vehicle positions as onboard telematics become available.
5. **Low-Data / WhatsApp & PWA Channels**: Expose the same `/api/v1/chat` agent over WhatsApp and installable offline-capable PWA shells for low-bandwidth commuter access.


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


