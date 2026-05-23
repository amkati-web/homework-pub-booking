# Ex7 — Handoff bridge

## Your answer

The HandoffBridge sits one level above both halves and owns the
round-trip state machine. It is not itself a Half — it has no
discover() or tool registry. Its only job is deciding which half
runs next and what input it receives.

Each round follows this sequence: loop runs with current_input →
if next_action=handoff_to_structured, bridge packages the loop
result into a Handoff via build_forward_handoff() and writes it
atomically to ipc/handoff_to_structured.json → structured half
runs with {"data": handoff.data} → if next_action=complete the
session is marked done; if next_action=escalate the bridge calls
build_reverse_task() and loops back with a new current_input.

The reverse-task path is the architecturally interesting part.
build_reverse_task() rewrites the input as:
  {"task": "structured half rejected. Reason: <reason>. Produce
   an alternative.", "context": {"prior_result": ...,
   "rejection_reason": ..., "retry": True}}
This gives the loop half the rejection reason explicitly so a real
LLM can choose a different venue, smaller party, or lower deposit.
In the scripted offline demo the second round hardcodes royal_oak
(16 seats, deposit under £300) to keep the test deterministic.

Three design decisions worth explaining: (1) Stale IPC files from
the previous round are moved to logs/handoffs/round_N_forward.json
rather than deleted — this preserves the audit trail and means a
crash mid-round leaves evidence. (2) Every half transition emits a
session.state_changed trace event so make narrate-latest can
reconstruct the full round-trip in English without reading code.
(3) The bridge returns BridgeResult with outcome="max_rounds_exceeded"
rather than raising — the caller decides whether that is fatal.

The max_rounds=3 cap prevents infinite loops when the structured
half rejects every proposal. In production this would trigger
human escalation; in the homework it surfaces as a failed session
with a clear reason in the trace.

Session sess_ad4a97312596 showed the expected two-round pattern:
round 1 loop proposed haymarket_tap → structured rejected (party
too large) → round 2 loop proposed royal_oak → structured confirmed
ref=BK-7D401E9E.

## Citations

- starter/handoff_bridge/bridge.py — HandoffBridge.run + helpers
- starter/handoff_bridge/run.py — scripted offline scenario
- starter/handoff_bridge/integrity.py — verify_dataflow
- sess_ad4a97312596 — two-round offline run confirming rejection+retry