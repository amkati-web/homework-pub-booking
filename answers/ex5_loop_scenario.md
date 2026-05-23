# Ex5 — Edinburgh research loop scenario

## Your answer
# Ex5 — Edinburgh research loop scenario

## Your answer

### Offline run (scripted FakeLLMClient)

The offline run used a scripted FakeLLMClient and completed successfully.
The planner produced two subgoals: sg_1 (research venues near Haymarket
for a party of 6) and sg_2 (produce a flyer with the chosen venue,
weather, and cost). Both ran in the same executor session.

The tool call sequence was exactly as required:
1. venue_search(near='Haymarket', party_size=6, budget_max_gbp=800)
   → found 1 result: Haymarket Tap (seats 8, hire fee £0, min spend £200)
2. get_weather(city='edinburgh', date='2026-04-25')
   → condition: cloudy, temperature_c: 12
3. calculate_cost(venue_id='haymarket_tap', party_size=6, duration_hours=3,
   catering_tier='bar_snacks')
   → subtotal £324, service £32, total £556, deposit £111
4. generate_flyer(event_details={...})
   → wrote workspace/flyer.html (2091 bytes)
5. complete_task()

The dataflow integrity check passed: 4 facts verified against tool outputs
(£556 total, £111 deposit, cloudy condition, 12°C temperature).


### Real LLM run (Qwen3-32B via Nebius)

Session sess_03223b0d9d7c demonstrated the classic spiral failure described
in docs/real-mode-failures.md. The executor ignored the required tool
sequence and called venue_search four times with wrong parameters:

1. venue_search(near='Old Town', party_size=50) → 0 results
2. venue_search(near='Edinburgh City Centre', party_size=45) → 0 results
3. venue_search(near='Grassmarket', party_size=50, budget_max_gbp=1500) → 0 results
4. venue_search(near='Edinburgh Castle', party_size=40, budget_max_gbp=2000) → 0 results

Two compounding errors caused the spiral:
- Wrong party size (40-50 instead of 6) — the LLM hallucinated a much
  larger group, so all venue searches returned 0 results
- Wrong area (Old Town/Grassmarket/Castle instead of Haymarket) — ignored
  the explicit constraint in the task description

After four failed searches the executor called handoff_to_structured with
reason "No venues found after multiple searches; need human input to adjust
criteria". generate_flyer was never called, so no flyer was written and
the scenario failed.

The planner ran at 23:07:33 UTC and produced 2 subgoals. The first tool
call was at 23:08:25 UTC — 52 seconds of planning before spiralling.
The handoff_to_structured was called at 23:08:50 UTC — the entire spiral
took under 30 seconds across 4 tool calls.

## Citations

- sess_03223b0d9d7c — real LLM run, spiral failure
  C:\Users\Ekaterina\AppData\Local\sovereign-agent\examples\ex5-edinburgh-research\sess_03223b0d9d7c\logs\trace.jsonl
- Offline run sessions visible in AppData\Local\Temp (FakeLLMClient,
  dataflow OK: 4 facts verified)


## Fabrication test

The dataflow integrity check catches fabricated values. Changing £556 to
£9999 in the flyer causes verify_dataflow to return ok=False with
unverified_facts=['£9999'], because 9999 does not appear in any tool
output in _TOOL_CALL_LOG. The check strips £ and °C before comparing,
so it matches on the raw numeric value against tool outputs.


