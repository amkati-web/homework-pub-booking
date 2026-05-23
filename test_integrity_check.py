from starter.edinburgh_research.integrity import clear_log, record_tool_call, verify_dataflow

# Test 1: scorching temperature
clear_log()
record_tool_call(
    "get_weather", {"city": "Edinburgh"}, {"temperature": 35, "condition": "scorching"}
)
r = verify_dataflow('<dd data-testid="weather">scorching 35C</dd>')
print("scorching 35C:", r.ok, "|", r.summary)

# Test 2: fake venue
clear_log()
record_tool_call("venue_search", {}, {"results": [{"name": "The Haymarket Bar"}]})
r = verify_dataflow('<span data-testid="venue_name">Castle Royal Grand Inn</span>')
print("fake venue:", r.ok, "|", r.summary)
