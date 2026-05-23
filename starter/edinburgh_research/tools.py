"""Ex5 tools. Four tools the agent uses to research an Edinburgh booking."""

from __future__ import annotations

import json
from pathlib import Path

from sovereign_agent.session.directory import Session
from sovereign_agent.tools.registry import ToolError, ToolRegistry, ToolResult, _RegisteredTool

from .integrity import record_tool_call

_SAMPLE_DATA = Path(__file__).parent / "sample_data"

SA_TOOL_DEPENDENCY_MISSING = "SA_TOOL_DEPENDENCY_MISSING"
SA_TOOL_INVALID_INPUT = "SA_TOOL_INVALID_INPUT"


def venue_search(near: str, party_size: int, budget_max_gbp: int = 1000) -> ToolResult:
    """Search for Edinburgh venues near <near> that can seat the party."""
    data_file = _SAMPLE_DATA / "venues.json"
    if not data_file.exists():
        raise ToolError(SA_TOOL_DEPENDENCY_MISSING, f"venues.json not found at {data_file}")

    venues = json.loads(data_file.read_text())
    results = [
        v
        for v in venues
        if v.get("open_now")
        and near.lower() in v.get("area", "").lower()
        and v.get("seats_available_evening", 0) >= party_size
        and (v.get("hire_fee_gbp", 0) + v.get("min_spend_gbp", 0)) <= budget_max_gbp
    ]
    output = {"near": near, "party_size": party_size, "results": results, "count": len(results)}
    record_tool_call(
        "venue_search",
        {"near": near, "party_size": party_size, "budget_max_gbp": budget_max_gbp},
        output,
    )
    return ToolResult(
        success=True,
        output=output,
        summary=f"venue_search({near}, party={party_size}): {len(results)} result(s)",
    )


def get_weather(city: str, date: str) -> ToolResult:
    """Look up the scripted weather for <city> on <date> (YYYY-MM-DD)."""
    data_file = _SAMPLE_DATA / "weather.json"
    if not data_file.exists():
        raise ToolError(SA_TOOL_DEPENDENCY_MISSING, f"weather.json not found at {data_file}")

    weather_data = json.loads(data_file.read_text())
    city_data = weather_data.get(city.lower())
    if not city_data:
        output = {"error": f"city '{city}' not found"}
        record_tool_call("get_weather", {"city": city, "date": date}, output)
        return ToolResult(
            success=False, output=output, summary=f"get_weather({city}, {date}): city not found"
        )

    day = city_data.get(date)
    if not day:
        output = {"error": f"date '{date}' not found for city '{city}'"}
        record_tool_call("get_weather", {"city": city, "date": date}, output)
        return ToolResult(
            success=False, output=output, summary=f"get_weather({city}, {date}): date not found"
        )

    output = {"city": city, "date": date, **day}
    record_tool_call("get_weather", {"city": city, "date": date}, output)
    return ToolResult(
        success=True,
        output=output,
        summary=f"get_weather({city}, {date}): {day['condition']}, {day['temperature_c']}C",
    )


def calculate_cost(
    venue_id: str,
    party_size: int,
    duration_hours: int,
    catering_tier: str = "bar_snacks",
) -> ToolResult:
    """Compute the total cost for a booking."""
    data_file = _SAMPLE_DATA / "catering.json"
    if not data_file.exists():
        raise ToolError(SA_TOOL_DEPENDENCY_MISSING, f"catering.json not found at {data_file}")

    catering = json.loads(data_file.read_text())
    base_per_head = catering["base_rates_gbp_per_head"][catering_tier]
    venue_mult = catering["venue_modifiers"].get(venue_id, 1.0)
    service_pct = catering["service_charge_percent"]

    venues_file = _SAMPLE_DATA / "venues.json"
    venues = json.loads(venues_file.read_text())
    venue = next((v for v in venues if v["id"] == venue_id), None)
    hire_fee = venue["hire_fee_gbp"] if venue else 0
    min_spend = venue["min_spend_gbp"] if venue else 0

    subtotal = int(base_per_head * venue_mult * party_size * max(1, duration_hours))
    service = int(subtotal * service_pct / 100)
    total = subtotal + service + hire_fee + min_spend

    if total < 300:
        deposit = 0
    elif total <= 1000:
        deposit = int(total * 0.20)
    else:
        deposit = int(total * 0.30)

    output = {
        "venue_id": venue_id,
        "party_size": party_size,
        "duration_hours": duration_hours,
        "catering_tier": catering_tier,
        "subtotal_gbp": subtotal,
        "service_gbp": service,
        "total_gbp": total,
        "deposit_required_gbp": deposit,
    }
    record_tool_call(
        "calculate_cost",
        {
            "venue_id": venue_id,
            "party_size": party_size,
            "duration_hours": duration_hours,
            "catering_tier": catering_tier,
        },
        output,
    )
    return ToolResult(
        success=True,
        output=output,
        summary=f"calculate_cost({venue_id}, {party_size}): total £{total}, deposit £{deposit}",
    )


def generate_flyer(session: Session, event_details: dict) -> ToolResult:
    """Produce an HTML flyer and write it to workspace/flyer.html."""
    venue_name = event_details.get("venue_name", "TBC")
    venue_address = event_details.get("venue_address", "TBC")
    date = event_details.get("date", "TBC")
    time = event_details.get("time", "TBC")
    party_size = event_details.get("party_size", "TBC")
    condition = event_details.get("condition", "TBC")
    temperature_c = event_details.get("temperature_c", "TBC")
    total_gbp = event_details.get("total_gbp", "TBC")
    deposit_required_gbp = event_details.get("deposit_required_gbp", "TBC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Event at {venue_name}</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; border: 2px solid #333; }}
  h1 {{ color: #2c3e50; }}
  dl {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
  dt {{ font-weight: bold; color: #555; }}
  dd {{ margin: 0; }}
</style>
</head>
<body>
  <h1>Event Booking</h1>
  <dl>
    <dt>Venue</dt><dd data-testid="venue_name">{venue_name}</dd>
    <dt>Address</dt><dd data-testid="venue_address">{venue_address}</dd>
    <dt>Date</dt><dd data-testid="date">{date}</dd>
    <dt>Time</dt><dd data-testid="time">{time}</dd>
    <dt>Party Size</dt><dd data-testid="party_size">{party_size}</dd>
    <dt>Weather</dt><dd data-testid="condition">{condition}</dd>
    <dt>Temperature</dt><dd data-testid="temperature_c">{temperature_c}C</dd>
    <dt>Total Cost</dt><dd data-testid="total">£{total_gbp}</dd>
    <dt>Deposit Required</dt><dd data-testid="deposit">£{deposit_required_gbp}</dd>
  </dl>
</body>
</html>"""

    out_path = session.workspace_dir / "flyer.html"
    out_path.write_text(html, encoding="utf-8")
    bytes_written = len(html)

    output = {"path": "workspace/flyer.html", "bytes_written": bytes_written}
    record_tool_call("generate_flyer", {"event_details": event_details}, output)
    return ToolResult(
        success=True,
        output=output,
        summary=f"generate_flyer: wrote workspace/flyer.html ({bytes_written} chars)",
    )


def build_tool_registry(session: Session) -> ToolRegistry:
    """Build a session-scoped tool registry with all four Ex5 tools."""
    from sovereign_agent.tools.builtin import make_builtin_registry

    reg = make_builtin_registry(session)

    reg.register(
        _RegisteredTool(
            name="venue_search",
            description="Search Edinburgh venues by area, party size, and max budget.",
            fn=venue_search,
            parameters_schema={
                "type": "object",
                "properties": {
                    "near": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "budget_max_gbp": {"type": "integer", "default": 1000},
                },
                "required": ["near", "party_size"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,
            examples=[
                {
                    "input": {"near": "Haymarket", "party_size": 6, "budget_max_gbp": 800},
                    "output": {"count": 1, "results": [{"id": "haymarket_tap"}]},
                }
            ],
        )
    )

    reg.register(
        _RegisteredTool(
            name="get_weather",
            description="Get scripted weather for a city on a YYYY-MM-DD date.",
            fn=get_weather,
            parameters_schema={
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "date": {"type": "string"},
                },
                "required": ["city", "date"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,
            examples=[
                {
                    "input": {"city": "Edinburgh", "date": "2026-04-25"},
                    "output": {"condition": "cloudy", "temperature_c": 12},
                }
            ],
        )
    )

    reg.register(
        _RegisteredTool(
            name="calculate_cost",
            description="Compute total cost and deposit for a booking.",
            fn=calculate_cost,
            parameters_schema={
                "type": "object",
                "properties": {
                    "venue_id": {"type": "string"},
                    "party_size": {"type": "integer"},
                    "duration_hours": {"type": "integer"},
                    "catering_tier": {
                        "type": "string",
                        "enum": [
                            "drinks_only",
                            "bar_snacks",
                            "sit_down_meal",
                            "three_course_meal",
                        ],
                        "default": "bar_snacks",
                    },
                },
                "required": ["venue_id", "party_size", "duration_hours"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=True,
            examples=[
                {
                    "input": {
                        "venue_id": "haymarket_tap",
                        "party_size": 6,
                        "duration_hours": 3,
                    },
                    "output": {"total_gbp": 540, "deposit_required_gbp": 0},
                }
            ],
        )
    )

    def _flyer_adapter(event_details: dict) -> ToolResult:
        return generate_flyer(session, event_details)

    reg.register(
        _RegisteredTool(
            name="generate_flyer",
            description="Write an HTML flyer for the event to workspace/flyer.html.",
            fn=_flyer_adapter,
            parameters_schema={
                "type": "object",
                "properties": {"event_details": {"type": "object"}},
                "required": ["event_details"],
            },
            returns_schema={"type": "object"},
            is_async=False,
            parallel_safe=False,
            examples=[
                {
                    "input": {
                        "event_details": {
                            "venue_name": "Haymarket Tap",
                            "date": "2026-04-25",
                            "party_size": 6,
                        }
                    },
                    "output": {"path": "workspace/flyer.html"},
                }
            ],
        )
    )

    return reg


__all__ = [
    "build_tool_registry",
    "venue_search",
    "get_weather",
    "calculate_cost",
    "generate_flyer",
]
