---
name: meeting-listener
description: Record a live meeting from the Mac mic, then transcribe and produce a structured summary (TL;DR, decisions, action items, client/prospect signals, notable quotes). Triggers on "start the meeting listener", "record this meeting", "listen to my call", "stop the meeting", "summarize the meeting I just recorded", or "how did I do on that call" (post-call self-review). Outputs land in meetings/YYYY-MM-DD-<name>/.
---

# Meeting Listener

Wraps the recorder script `tools/meeting_listener.py` (ships with this repo; the skill also works manually without it: record with any app, drop the audio file in the meeting folder, and start at the transcription step). The script runs ffmpeg as a detached background process so the operator triggers start/stop from chat without touching Terminal, then transcribes (local Whisper, or Groq if `GROQ_API_KEY` is set) and summarizes via `tools/openrouter_client.py`.

## Trigger phrases → command

| Operator says… | Run… |
|---|---|
| "start the meeting listener", "record this meeting", "start recording" | `python3 tools/meeting_listener.py start "<name>"` |
| "stop the meeting", "end the recording", "summarize what you heard" | `python3 tools/meeting_listener.py stop` |
| "is the recording still going?" | `python3 tools/meeting_listener.py status` |

## Handling `start`

1. No meeting name given → ask for one short slug (e.g. `acme-discovery-call`, `internal-planning`). Refused → default to `meeting`.
2. Run `start`. The script should return within seconds with a PID confirming recording is live.
3. Tell the operator: "Recording is running in the background. When the meeting ends, say 'stop the meeting' and I'll transcribe it and write the summary."
4. **Do not** keep the chat turn open waiting — the recorder is detached and survives across turns.

## Handling `stop`

1. Run `stop`. It blocks while it kills ffmpeg cleanly, transcribes (local Whisper on-device, or a hosted Whisper API if a key is set — much faster), and generates the structured summary via an LLM call (`tools/openrouter_client.py` works here).
2. Print the summary verbatim.
3. Link to `meetings/YYYY-MM-DD-<name>/summary.md`.
4. If this was a client or prospect meeting: offer to log an activity note in the client record, update the contact stage in <TASK SYSTEM>, and create pain-point notes from anything in the Client Signals section.

## Pre-flight checklist (one-time setup)

- `ffmpeg` installed — `which ffmpeg`
- Whisper installed — `python3 -c "import whisper"`; failing that, `pip3 install -U openai-whisper`
- An LLM API key in `.env` for the summary (referenced by variable name, never pasted)
- macOS mic permission granted to the terminal app running the agent: System Settings → Privacy & Security → Microphone

## Output structure

```
meetings/YYYY-MM-DD-<meeting-name>/
  ├── audio.wav        # 16 kHz mono
  ├── transcript.txt   # raw transcription output
  ├── summary.md       # structured summary
  └── ffmpeg.log       # recording debug log
```

## Summary sections

TL;DR → Key Topics → Decisions → Action Items (Owner | Action | Due Date) → Client/Prospect Signals → Open Questions for the operator → Notable Quotes.

## Post-call self-review ("how did I do on that call?")

1. Read `transcript.txt` from the meeting folder (ambiguous → default to the most recent folder in `meetings/`; confirm with the operator).
2. Analyze the OPERATOR'S side of the conversation as a founder sales/client call — discovery, framing, objection handling — not corporate-meeting facilitation. Produce exactly three sections:
   - **Strengths** — 2-3 concrete moments that worked, each with a short transcript quote
   - **Missed signals** — buying signals, objections, pain points, or upsell openings that went unaddressed; hedging where a direct ask was warranted. Quote the moment.
   - **One improvement** — the single highest-leverage change for the next call. One, not five.
3. Append the review to the meeting folder's `summary.md` under `## Post-call self-review`.
4. Evidence discipline: quote real transcript lines only — never invent moments. No speaker labels in the transcript → say so and caveat the speaking-pattern analysis.

## Failure modes

| Symptom | Fix |
|---|---|
| `start` reports ffmpeg exited immediately | macOS mic permission missing — enable it for the terminal app |
| `start` says "already running" | A previous session is still active — run `stop` first, or `status` to inspect |
| `stop` says "no active recording" | Lockfile deleted or ffmpeg crashed — check the recorder's lockfile and the latest folder's `ffmpeg.log` |
| Whisper import error | `pip3 install -U openai-whisper` in the same Python that runs the script |
| Transcription feels slow | Add a hosted Whisper API key to `.env` — local transcription runs at roughly 10-20% of real-time on Apple Silicon |

## Cost per meeting

Local Whisper is free; the LLM summary of a 1-hour transcript costs a few cents on a mid-tier model.
