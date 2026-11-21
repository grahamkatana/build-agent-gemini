from collections import defaultdict
from typing import Any
from sqlalchemy import bindparam, text

from src.database.db import engine
from src.schemas.chat import RouteMapData, RouteReference


def fetch_routes_and_map_data(
    route_codes: list[str],
    include_map_data: bool = True,
) -> tuple[list[RouteReference], list[RouteMapData]]:
    if not route_codes:
        return [], []

    routes_sql = text("""
        SELECT route_code, name, region, terminus_from, terminus_to
        FROM routes
        WHERE route_code IN :codes
    """).bindparams(bindparam("codes", expanding=True))

    stops_sql = text("""
        SELECT route_code, direction, sequence_no, name, street, stop_type,
               CAST(lon AS FLOAT) AS lon,
               CAST(lat AS FLOAT) AS lat,
               variant_code
        FROM stops
        WHERE route_code IN :codes
          AND lon IS NOT NULL
          AND lat IS NOT NULL
        ORDER BY route_code, direction, variant_code NULLS FIRST, sequence_no ASC
    """).bindparams(bindparam("codes", expanding=True))

    with engine.connect() as conn:
        route_rows = conn.execute(routes_sql, {"codes": route_codes}).mappings().all()
        if not route_rows:
            return [], []

        valid_codes = [r["route_code"] for r in route_rows]
        stop_rows = (
            conn.execute(stops_sql, {"codes": valid_codes}).mappings().all()
            if include_map_data
            else []
        )

    route_refs = [
        RouteReference(
            route_code=r["route_code"],
            name=r["name"],
            region=r["region"],
            terminus_from=r["terminus_from"],
            terminus_to=r["terminus_to"],
        )
        for r in route_rows
    ]

    if not include_map_data:
        return route_refs, []

    stops_by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for s in stop_rows:
        stops_by_route[s["route_code"]].append(dict(s))

    map_routes: list[RouteMapData] = []
    for r in route_rows:
        code = r["route_code"]
        route_stops = stops_by_route.get(code, [])
        if not route_stops:
            continue

        features: list[dict[str, Any]] = []
        lines_by_dir_variant: dict[tuple[str, str | None], list[list[float]]] = (
            defaultdict(list)
        )
        all_lons: list[float] = []
        all_lats: list[float] = []

        for s in route_stops:
            coord = [s["lon"], s["lat"]]
            all_lons.append(s["lon"])
            all_lats.append(s["lat"])

            lines_by_dir_variant[(s["direction"], s["variant_code"])].append(coord)

            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": coord,
                    },
                    "properties": {
                        "feature_kind": "stop",
                        "route_code": code,
                        "direction": s["direction"],
                        "variant_code": s["variant_code"],
                        "sequence_no": s["sequence_no"],
                        "name": s["name"],
                        "street": s["street"] or "",
                        "stop_type": s["stop_type"],
                    },
                }
            )

        # Build LineString path per (direction, variant_code)
        for (direction, variant_code), coords in lines_by_dir_variant.items():
            if len(coords) >= 2:
                features.insert(
                    0,
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coords,
                        },
                        "properties": {
                            "feature_kind": "route_path",
                            "route_code": code,
                            "route_name": r["name"],
                            "direction": direction,
                            "variant_code": variant_code,
                        },
                    },
                )

        bbox = [min(all_lons), min(all_lats), max(all_lons), max(all_lats)]
        map_routes.append(
            RouteMapData(
                route_code=code,
                name=r["name"],
                region=r["region"],
                bbox=bbox,
                geojson={
                    "type": "FeatureCollection",
                    "features": features,
                },
            )
        )

    return route_refs, map_routes
