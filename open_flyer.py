import asyncio
import os
import pathlib
import sys

sys.path.insert(0, ".")

from starter.edinburgh_research import run
from starter.edinburgh_research.integrity import _TOOL_CALL_LOG

# Run the scenario
asyncio.run(run.run_scenario(real=False))

# Get event details from tool call log
for record in _TOOL_CALL_LOG:
    if record.tool_name == "generate_flyer":
        d = record.arguments["event_details"]

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Edinburgh Pub Booking</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; background: #f9f9f9; }}
    article {{ background: white; border-radius: 8px; padding: 32px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    h1 {{ color: #2c3e50; border-bottom: 2px solid #e67e22; padding-bottom: 12px; }}
    dl {{ display: grid; grid-template-columns: 160px 1fr; gap: 8px 16px; }}
    dt {{ font-weight: bold; color: #777; }}
    dd {{ margin: 0; color: #2c3e50; }}
    .section {{ background: #fef9e7; border-left: 4px solid #e67e22; padding: 12px 16px; margin-top: 16px; border-radius: 4px; }}
  </style>
</head>
<body>
  <article>
    <h1>Edinburgh Pub Night</h1>
    <dl>
      <dt>Venue</dt><dd data-testid="venue-name">{d["venue_name"]}</dd>
      <dt>Address</dt><dd data-testid="venue-address">{d["venue_address"]}</dd>
      <dt>Date</dt><dd data-testid="date">{d["date"]}</dd>
      <dt>Time</dt><dd data-testid="time">{d["time"]}</dd>
      <dt>Party size</dt><dd data-testid="party-size">{d["party_size"]}</dd>
    </dl>
    <div class="section">
      <dl>
        <dt>Weather</dt><dd data-testid="weather-condition">{d["condition"]}</dd>
        <dt>Temperature</dt><dd data-testid="temperature">{d["temperature_c"]}C</dd>
      </dl>
    </div>
    <div class="section">
      <dl>
        <dt>Total cost</dt><dd data-testid="total-cost">{d["total_gbp"]}</dd>
        <dt>Deposit</dt><dd data-testid="deposit">{d["deposit_required_gbp"]}</dd>
      </dl>
    </div>
  </article>
</body>
</html>"""

        flyer_path = pathlib.Path("flyer.html")
        flyer_path.write_text(html, encoding="utf-8")
        print(f"Flyer saved to: {flyer_path.absolute()}")
        os.startfile(str(flyer_path.absolute()))
        break
