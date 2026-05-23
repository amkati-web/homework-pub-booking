# Ex8 — Voice pipeline

## Your answer

The voice pipeline implements two modes that share an identical
trace-event contract. Text mode (run_text_mode) reads from stdin and
writes to stdout. Voice mode (run_voice_mode) replaces the transport
layer with mic capture → Speechmatics STT → Rime TTS, but emits
the same voice.utterance_in and voice.utterance_out events with
payload {text, turn, mode}. The mode field records which transport
ran; everything downstream is identical.

The audio pipeline in voice mode is: sounddevice captures 16-bit PCM
mono at 16kHz → silence detection via RMS threshold ends each
utterance after SILENCE_TIMEOUT_S=2.0s of quiet or MAX_UTTERANCE_S=15s
total → raw PCM bytes sent to Speechmatics realtime websocket
(wss://eu2.rt.speechmatics.com/v2) → final transcripts collected →
ManagerPersona.respond() called → Rime Arcana TTS returns MP3 →
pydub decodes MP3 to PCM → sounddevice plays back.

Graceful degradation is a first-class design concern. If
SPEECHMATICS_KEY is missing, run_voice_mode logs a warning and
falls through to run_text_mode rather than crashing. If RIME_API_KEY
is missing, STT and manager reply still work but the reply is printed
rather than spoken. If sounddevice or speechmatics-python are not
installed, the ImportError is caught and text mode is used with an
install hint. This means CI passes the graded check without any
voice credentials.

The ManagerPersona accumulates full conversation history across turns
and prepends it as system+user+assistant messages on every LLM call.
This lets Alasdair remember the party size and deposit from earlier
in the conversation — tested in session sess_e220a68d21e9 where he
accepted a party of 6 at £200 deposit ("Aye, we can do that") and
remembered the booking when asked to confirm ("You're booked for
7:30 tonight").

Three design decisions worth noting: (1) The stable sender pattern
from Ex6 is not needed here because each conversation is a fresh
session with its own history list. (2) Audio is saved to
workspace/turn_N_input.wav for debugging — this was essential for
diagnosing RMS threshold issues on different microphones. (3) The
Speechmatics client is synchronous so it runs in an executor to
avoid blocking the asyncio event loop.

Text mode is the primary gradeable path. The full voice pipeline
requires SPEECHMATICS_KEY + RIME_API_KEY + portaudio, but the
architecture is identical — only the I/O layer changes.

## Citations

- starter/voice_pipeline/voice_loop.py — run_voice_mode, _record_until_silence,
  _transcribe_speechmatics, _speak_rime
- starter/voice_pipeline/manager_persona.py — ManagerPersona, history management
- starter/voice_pipeline/run.py — entry point, dotenv loading
- sess_e220a68d21e9 — text mode run: party of 6, £200 deposit, accepted