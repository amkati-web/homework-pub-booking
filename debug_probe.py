from starter.edinburgh_research.integrity import (
    verify_dataflow,
    extract_temperature_facts,
    extract_condition_facts,
    check_plausibility,
    clear_log,
)

clear_log()  # empty log, exactly like the probe

bad_value = "scorching 35C"
fake_flyer = (
    "# Booking flyer\n\n"
    "Venue: Haymarket Tap\n"
    "Party of 6 at 19:30, 2026-04-25.\n"
    "Weather: cloudy, 12C.\n"
    f"Total: {bad_value}.\n"
    "Deposit: £0.\n"
)
print("flyer:", repr(fake_flyer))
print("temps:", extract_temperature_facts(fake_flyer))
print("conditions:", extract_condition_facts(fake_flyer))
temps = extract_temperature_facts(fake_flyer)
conds = extract_condition_facts(fake_flyer)
print("plausibility on temps:", check_plausibility(temps))
print("plausibility on conds:", check_plausibility(conds))
print("plausibility on both:", check_plausibility(temps + conds))
result = verify_dataflow(fake_flyer)
print("ok:", result.ok)
print("unverified:", result.unverified_facts)
print("summary:", result.summary)
