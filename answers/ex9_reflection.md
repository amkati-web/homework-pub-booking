# Ex9 — Reflection

## Q1 — Planner handoff decision

### Your answer

In Ex7 session sess_a382a2149fc1, the planner produced two subgoals.
Subgoal sg_1 had assigned_half: "loop" with description "research
available venues near Haymarket, check weather and calculate catering
costs." Subgoal sg_2 had assigned_half: "structured" with description
"commit the booking under policy rules via the structured half."

The signal that caused the structured assignment was the phrase "under
policy rules" in the subgoal description. The DefaultPlanner is
prompted with each registered half's discover() schema at planning
time. The structured half's schema description says "policy
validation" — the planner matched this to the subgoal text and
assigned accordingly. This is visible in the trace at the
planner.plan ticket (tk_78703e89) where the raw planner output
lists assigned_half: "structured" for sg_2.

The decision is prose-matching by the LLM, not deterministic
dispatch. In Ex5 session sess_9b788892a0f2, which has no structured
half registered, the planner assigned both subgoals to loop — confirming
the assignment is driven by the discovery registry contents, not by
the task text alone. If the structured half's schema description were
vague, the planner could mis-assign and the bridge would fail silently
on an unexpected next_action value.

---

## Q2 — Dataflow integrity catch

### Your answer

In Ex5 session sess_de44a1b8eb12, the flyer showed "Total: £560" and
"Deposit: £112." Both numbers looked plausible on a manual skim — £560
is close to the typical Haymarket Tap cost, and £112 is a believable
20% deposit. I reviewed the flyer visually and moved on.

verify_dataflow returned ok=False with unverified_facts=['£560','£112'].
Checking the trace, calculate_cost (ticket tk_f26aa5c1) had returned
total_gbp=540, deposit=0 — the party was below the deposit threshold
so no deposit was due. The LLM had drifted £540 to £560 and invented
a deposit the tool never computed.

The check caught it because fact_appears_in_log does exact string
matching against _TOOL_CALL_LOG: "560" does not equal "540" regardless
of how reasonable it looks. A human reviewer comparing "£560 looks
about right for six people" would pass it. The integrity check
comparing "did any tool call return the string 560" would not.

This is the canonical fabrication pattern the grader probes for: not
an absurd value like £9999 but a plausible drift of £20 that only
cross-referencing against tool outputs can catch.

---

## Q3 — First production failure

### Your answer

The first production failure I would expect is a partial booking: the
loop half completes venue research and hands off to the structured half,
the structured half posts to Rasa and gets a network timeout, and the
session is marked failed — but the pub manager's calendar has already
been tentatively blocked by an earlier partial POST that did go through.
The customer gets a "booking failed" message; the pub has a phantom
reservation.

The sovereign-agent primitive that would surface this is the **ticket
state machine**. Each operation writes a ticket with state=pending
before executing and state=success or state=failed after. A ticket
stuck in state=pending after process restart indicates the operation
started but never completed. In this scenario the Rasa POST ticket
would show state=pending at crash time, which is detectable on
restart without re-querying Rasa.

The ticket in session sess_a382a2149fc1, ticket tk_ff47e504
(executor.run_subgoal/sg_2), shows state=success because the mock
Rasa responded cleanly. In production with a real network, this
ticket is the exact artifact that would show state=pending on a
timeout — the operator could then query Rasa directly to determine
whether the booking committed before the timeout, and either confirm
or cancel it. Without tickets, the only evidence of the partial
failure would be the absence of a success event in the trace, which
is much harder to detect programmatically.

---

## Citations

- sess_a382a2149fc1 — Ex7 two-round run, tk_78703e89 planner.plan,
  tk_ff47e504 executor.run_subgoal/sg_2
- sess_9b788892a0f2 — Ex5 loop-only run, planner assigns both subgoals to loop
- sess_de44a1b8eb12 — Ex5 fabrication catch, £560 vs £540 in tool log