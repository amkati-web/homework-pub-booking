# Ex6 — Rasa structured half

## Your answer

The RasaStructuredHalf subclass overrides run() to POST a booking
intent to Rasa's REST webhook and interpret the response. The data
flow is: loop half produces raw booking dict → normalise_booking_payload
in validator.py canonicalises types (str party_size → int, "7:30pm" →
"19:30", "£200" → 200) and produces a Rasa-shaped message with a
stable sender_id derived from SHA-1(venue+date+time) → urllib POST to
/webhooks/rest/webhook → parse response messages for custom slot
{action: committed} or {action: rejected} → return HalfResult with
next_action="complete" or next_action="escalate".

For offline mode a stdlib ThreadingHTTPServer thread mimics the Rasa
webhook, applying the same validation rules as ActionValidateBooking:
party_size <= 8, deposit_gbp <= 300. It returns a deterministic
booking reference BK-{SHA1[:8]} of venue+date+time+party. This lets
the full HTTP contract — normalisation, POST, response parsing — be
verified without a Rasa license. Session sess_4077b962809a confirmed
ref=BK-7D401E9E in offline mode.

For real mode, three terminals are required: action server on :5055,
Rasa server on :5005, and the scenario runner. Training required two
non-obvious fixes: (1) endpoints.yml model_groups must be a list with
a nested models: list, not a dict — Rasa's schema changed in 3.16+;
(2) the embedding model had to be Qwen/Qwen3-Embedding-8B (the only
model available on this Nebius account) rather than the documented
BAAI/bge-en-icl. Flow retrieval trained successfully after both fixes.
Session sess_304d0cbda9c9 confirmed ref=BK-7D401E9E via real Rasa CALM.

Flow triggering was unreliable via CompactLLMCommandGenerator because
embedding-based flow retrieval degraded at inference time even after
training. Fix: added nlu_triggers: - intent: confirm_booking to
flows.yml, added the intent to domain.yml, and created nlu.yml with
three training examples. This routes /confirm_booking through Rasa's
classic NLU intent matching rather than the LLM command generator —
correct for a programmatic entry point never typed by a human.

Three design decisions worth explaining: (1) ValidationFailed is caught
inside run() and returned as HalfResult(next_action="escalate") rather
than propagating — the StructuredHalf contract requires a result, not
an exception, so the bridge can decide whether to retry. (2) Network
errors (URLError, HTTPError, TimeoutError) each return a distinct
error_code (SA_EXT_SERVICE_UNAVAILABLE, SA_EXT_TIMEOUT) so callers
can apply different retry policies. (3) The stable sender_id means the
Rasa tracker accumulates a consistent conversation history across retries
within one session, which matters for CALM's slot-filling logic.

The mock server is not just a test convenience — it is the correct
offline-first design. Students without a Rasa license can validate the
full HTTP contract. The real Rasa path then adds only the CALM flow
and NLU layers on top of an already-verified wire protocol.

## Citations

- starter/rasa_half/validator.py — normalise_booking_payload + helpers
- starter/rasa_half/structured_half.py — RasaStructuredHalf.run + mock server
- rasa_project/data/flows.yml — confirm_booking flow with nlu_triggers
- rasa_project/domain.yml — slots, responses, actions
- rasa_project/actions/actions.py — ActionValidateBooking
- sess_4077b962809a — offline mock run, ref=BK-7D401E9E
- sess_304d0cbda9c9 — real Rasa run, ref=BK-7D401E9E