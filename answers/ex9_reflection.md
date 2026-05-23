# Ex9 — Reflection

## Q1 — Planner handoff decision

### Your answer

In Ex7 session sess_a382a2149fc1 the planner produced two subgoals:
sg_1 "research available venues near Haymarket, check weather and
catering costs" assigned to loop, and sg_2 "commit the booking under
policy rules" assigned to structured. The signal driving the
structured assignment was the phrase "under policy rules" in the
subgoal description — sovereign-agent's DefaultPlanner is prompted
with each half's discovery schema, and the structured half's schema
names "policy validation" as its purpose. The planner matched prose
to schema description.

This is an architectural risk, not a feature. The assignment is
advisory prose-matching by an LLM, not a type-checked dispatch. In
session sess_9b788892a0f2 (Ex5, loop-only) the planner correctly
assigned both subgoals to loop because no structured half was
registered — the planner cannot assign to a half that isn't in the
discovery registry. This confirms the assignment is driven by
registry contents, not hallucination.

The lesson: the planner's half-assignment decision is only as
reliable as the prose in each half's discover() schema. Vague
descriptions produce mismatch. The fix is to make the structured
half's schema description unambiguous about what it accepts — not
to trust the planner to infer it from context. Put the rules in
Python (ActionValidateBooking); the planner's job is routing, not
rule enforcement.

### Citation

- sess_a382a2149fc1 — Ex7 two-round run, sg_2 assigned to structured
- sess_9b788892a0f2 — Ex5 loop-only run, both subgoals stay in loop

---

## Q2 — Dataflow integrity catch

### Your answer

In Ex5 session sess_de44a1b8eb12 the flyer claimed "Total: £560" and
"Deposit: £112". Both numbers are plausible — £560 is close to the
real £540, and £112 is a believable 20% deposit. Manual review passed
them. verify_dataflow returned ok=False with unverified_facts=
['£560', '£112']. The trace showed calculate_cost returned
total_gbp=540, deposit=0 (below the deposit threshold). The LLM had
written £560 — a £20 drift from the tool output — and invented a
deposit that the tool never computed.

This is the canonical fabrication pattern: not an absurd number like
£9999 but a plausible drift that a human would accept on a skim.
The integrity check caught it because fact_appears_in_log does exact
string matching against _TOOL_CALL_LOG — "560" does not equal "540"
regardless of how reasonable it looks.

The broader lesson from building verify_dataflow: the check needs to
be grounded in tool outputs, not in plausibility. A check that asks
"does this look like a reasonable price for Edinburgh" would pass £560.
Only a check that asks "did any tool actually return this value" is
fabrication-proof. The planted-fabrication probe in the grader
(£9999, Castle Royal Grand Inn, scorching 35C) tests exactly this
distinction — two of the three require cross-referencing against
external ground truth (venues.json, Edinburgh climate bounds) rather
than the tool log, because the probe runs verify_dataflow with an
empty log.

### Citation

- sess_de44a1b8eb12 — Ex5 run with £560 fabrication caught
- sess_9b788892a0f2 — Ex5 clean run, 5 facts verified against tool log
- starter/edinburgh_research/integrity.py — fact_appears_in_log,
  check_plausibility, check_venue_names

---

## Q3 — Removing one framework primitive

### Your answer

I would keep session directories (Decision 1) and rebuild everything
else if forced. My reasoning is grounded in what actually happened
during debugging across these exercises.

In Ex7 the bridge failed silently on the first attempt — the IPC
file was written but the structured half read a stale copy from a
previous run. The fix took under two minutes: ls ipc/, cat the file,
compare timestamps. Without session directories this would have
required a debugger, breakpoints, and reconstructing state from
memory. With them it was archaeology with cat.

Tickets (Decision 3) I rebuilt mentally as append-only .jsonl lines
inside the session — the information is the same, the format is less
structured. Atomic-rename IPC (Decision 5) is replaceable by a
polling loop on a regular file with a lock. The forward-only state
machine (Decision 2) is important but it is enforced by code, not
by the directory structure.

Session directories are irreplaceable because they are the substrate
everything else runs on. Losing them means: cross-session data leaks
(two concurrent runs sharing state), no post-mortem debugging
("how did sess_de44a1b8eb12 produce £560" becomes impossible without
the workspace/flyer.html and trace.jsonl that recorded it), and no
make narrate-latest (the narrator reads trace.jsonl from the session
directory). The course slides compare session directories to git
commits — you can rebuild merge, diff, and blame from commits, but
not commits from the derived tools. The same inversion applies here:
tickets, IPC, and state machines can all be rebuilt given session
directories, but not the reverse.

### Citation

- sess_de44a1b8eb12 — Ex5 session with fabrication, workspace/flyer.html
  and trace.jsonl were the primary debugging artifacts
- sess_a382a2149fc1 — Ex7 two-round session, ipc/ directory used to
  diagnose stale handoff file
- sess_e220a68d21e9 — Ex8 text mode session, trace.jsonl confirmed
  voice.utterance_in and voice.utterance_out events emitted correctly