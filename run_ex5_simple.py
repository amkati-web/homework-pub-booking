import sys
import webbrowser
from pathlib import Path

from starter.edinburgh_research.integrity import clear_log, verify_dataflow
from starter.edinburgh_research.tools import (
    calculate_cost,
    generate_flyer,
    get_weather,
    venue_search,
)

sys.path.insert(0, str(Path(".").resolve()))

SAVE_DIR = Path.home() / "Desktop" / "ex5_flyer"
SAVE_DIR.mkdir(parents=True, exist_ok=True)


class S:
    workspace_dir = SAVE_DIR


clear_log()
print("[1/4] venue_search ...")
r1 = venue_search("Haymarket", 6, 800)
print("     ", r1.summary)
venue = r1.output["results"][0]
print("[2/4] get_weather ...")
r2 = get_weather("edinburgh", "2026-04-25")
print("     ", r2.summary)
print("[3/4] calculate_cost ...")
r3 = calculate_cost(venue["id"], 6, 3, "bar_snacks")
print("     ", r3.summary)
print("[4/4] generate_flyer ...")
r4 = generate_flyer(
    S(),
    {
        "venue_name": venue["name"],
        "venue_address": venue["address"],
        "date": "2026-04-25",
        "time": "19:30",
        "party_size": 6,
        "condition": r2.output["condition"],
        "temperature_c": r2.output["temperature_c"],
        "total_gbp": r3.output["total_gbp"],
        "deposit_required_gbp": r3.output["deposit_required_gbp"],
    },
)
print("     ", r4.summary)
flyer = (SAVE_DIR / "flyer.html").read_text(encoding="utf-8")
result = verify_dataflow(flyer)
print("Integrity:", result.summary)
webbrowser.open((SAVE_DIR / "flyer.html").as_uri())
print("Flyer saved to:", SAVE_DIR / "flyer.html")
