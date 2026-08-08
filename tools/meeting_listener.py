"""
meeting_listener.py — Meeting Recorder + Summarizer

Start/stop pattern designed to be driven from the terminal app running Claude
Code. You invoke `start` in one chat turn; recording runs in the background as
a detached process; you invoke `stop` in a later turn and it transcribes +
summarizes automatically. See .claude/skills/meeting-listener/SKILL.md.

Usage:
    python3 tools/meeting_listener.py start <meeting-name>
    python3 tools/meeting_listener.py stop
    python3 tools/meeting_listener.py status

    # Manual / power-user:
    python3 tools/meeting_listener.py transcribe <audio-path>
    python3 tools/meeting_listener.py summarize <transcript-path>

Output:
    meetings/YYYY-MM-DD-<name>/
        ├── audio.wav
        ├── transcript.txt
        └── summary.md

Requires:
    - ffmpeg (brew install ffmpeg)
    - Local Whisper (pip3 install -U openai-whisper) — no API key, runs locally
    - OPENROUTER_API_KEY in .env (for the LLM summary via tools/openrouter_client.py)
    - pip3 install requests python-dotenv

Optional:
    - GROQ_API_KEY in .env — uses Groq Whisper-large-v3-turbo (10x faster). The
      script auto-uses Groq if the key is present, otherwise falls back to local.
"""

import os
import sys
import signal
import subprocess
import datetime
import pathlib
import json
import time

from dotenv import load_dotenv

try:
    import requests
except ImportError:
    print("ERROR: pip3 install requests python-dotenv")
    sys.exit(1)

# Reuse the shared OpenRouter wrapper
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from openrouter_client import complete  # noqa: E402

load_dotenv()

WORKSPACE = pathlib.Path(__file__).resolve().parent.parent
MEETINGS_DIR = WORKSPACE / "meetings"
ACTIVE_FILE = MEETINGS_DIR / ".active.json"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SUMMARY_SYSTEM_PROMPT = """You are the operator's executive AI assistant at a marketing agency.
You are summarizing a meeting transcript. The transcript is from automatic speech
recognition and may contain errors — read through context, not literal text.

Output a single Markdown document with these sections, in this order:

# <Descriptive meeting title>

**Date:** <today>
**Duration (est.):** <from transcript length>
**Participants:** <best guess from transcript, or "Unclear">

## TL;DR
Three sentences max. What happened and what matters.

## Key Topics Discussed
Bulleted. One line per topic. Group related points.

## Decisions Made
Bulleted. Each item: what was decided, and (if stated) why.

## Action Items
Table with columns: Owner | Action | Due Date.
If owner or date unclear, say "Unclear" — never invent.

## Client / Prospect Signals
Only include if this appears to be a sales, discovery, or client-facing call.
Sub-bullets for: Pain points mentioned | Budget or pricing signals | Objections
or hesitations | Buying intent signals | Competitors named | Stated next step.

## Open Questions / Follow-Ups for the Operator
Things the meeting surfaced that need the operator's attention but weren't resolved.

## Raw Notable Quotes
2-5 short direct quotes worth preserving (customer pain, commitments, objections).

Rules:
- Use "we" when referring to the agency (the operator presents as a team).
- Never invent names, dates, dollar amounts, or commitments not in the transcript.
- If a section has nothing to report, write "None noted." — do not skip the section.
- Keep the whole summary under 800 words.
"""


# ============================================================================
# START / STOP / STATUS  (PID-file based, detached subprocess)
# ============================================================================

def _meeting_folder(name: str) -> pathlib.Path:
    today = datetime.date.today().isoformat()
    slug = name.lower().replace(" ", "-").replace("_", "-")
    folder = MEETINGS_DIR / f"{today}-{slug}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def cmd_start(name: str) -> None:
    """Launch ffmpeg recording in the background, detached. Returns immediately."""
    MEETINGS_DIR.mkdir(parents=True, exist_ok=True)

    if ACTIVE_FILE.exists():
        data = json.loads(ACTIVE_FILE.read_text())
        if _is_running(data["pid"]):
            print(f"WARNING: A recording is already running: '{data['name']}' (pid {data['pid']})")
            print("    Run `stop` first, or `status` to see details.")
            sys.exit(1)
        # Stale lockfile — clean it up.
        ACTIVE_FILE.unlink()

    folder = _meeting_folder(name)
    audio_path = folder / "audio.wav"
    log_path = folder / "ffmpeg.log"

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "avfoundation",
        "-i", ":0",               # :0 = default audio input on Mac
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        str(audio_path),
    ]

    log_f = open(log_path, "wb")
    # start_new_session=True detaches from the parent's process group so the
    # recording survives after the agent's command returns.
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=log_f,
        stderr=log_f,
        start_new_session=True,
    )

    # Give ffmpeg a second to actually start (so we catch mic-permission errors early).
    time.sleep(1.5)
    if proc.poll() is not None:
        # ffmpeg died immediately — surface the log.
        log_f.close()
        tail = log_path.read_text(errors="ignore")[-800:]
        print("ERROR: ffmpeg exited immediately. Last lines of log:\n")
        print(tail)
        print("\nMost common cause: macOS mic permission not granted to the terminal app running Claude Code.")
        print("System Settings → Privacy & Security → Microphone → enable Terminal/iTerm (whichever runs Claude Code).")
        sys.exit(1)

    ACTIVE_FILE.write_text(json.dumps({
        "pid": proc.pid,
        "name": name,
        "folder": str(folder),
        "audio": str(audio_path),
        "started_at": datetime.datetime.now().isoformat(timespec="seconds"),
    }, indent=2))

    print(f"Recording started: '{name}' (pid {proc.pid})")
    print(f"    Saving to: {audio_path}")
    print("    When the meeting is over, run: stop")


def cmd_status() -> None:
    if not ACTIVE_FILE.exists():
        print("No active recording.")
        return
    data = json.loads(ACTIVE_FILE.read_text())
    alive = _is_running(data["pid"])
    started = datetime.datetime.fromisoformat(data["started_at"])
    elapsed = datetime.datetime.now() - started
    mins = int(elapsed.total_seconds() // 60)
    secs = int(elapsed.total_seconds() % 60)
    audio = pathlib.Path(data["audio"])
    size_kb = audio.stat().st_size // 1024 if audio.exists() else 0
    status = "RUNNING" if alive else "DEAD (stale lockfile)"
    print(f"Meeting:    {data['name']}")
    print(f"Status:     {status}")
    print(f"Started:    {data['started_at']} ({mins}m {secs}s ago)")
    print(f"Audio size: {size_kb} KB")
    print(f"Folder:     {data['folder']}")


def cmd_stop() -> None:
    """Stop the background recording, transcribe, summarize, print summary."""
    if not ACTIVE_FILE.exists():
        print("No active recording to stop.")
        sys.exit(1)

    data = json.loads(ACTIVE_FILE.read_text())
    pid = data["pid"]
    folder = pathlib.Path(data["folder"])
    audio_path = pathlib.Path(data["audio"])
    name = data["name"]

    if _is_running(pid):
        print(f"Stopping recording (pid {pid})...")
        os.kill(pid, signal.SIGINT)   # ffmpeg closes the file cleanly on SIGINT
        # Wait up to 10 seconds for the file to finalize.
        for _ in range(20):
            time.sleep(0.5)
            if not _is_running(pid):
                break
        else:
            print("WARNING: ffmpeg didn't exit gracefully; sending SIGTERM.")
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    else:
        print("Note: ffmpeg already exited; proceeding to transcribe.")

    ACTIVE_FILE.unlink(missing_ok=True)

    if not audio_path.exists() or audio_path.stat().st_size < 1024:
        print(f"ERROR: audio file missing or too small: {audio_path}")
        sys.exit(1)
    print(f"Recording saved: {audio_path} ({audio_path.stat().st_size // 1024} KB)")

    transcript_path = folder / "transcript.txt"
    summary_path = folder / "summary.md"

    transcript = transcribe_audio(audio_path, transcript_path)
    summary = summarize_transcript(transcript, summary_path, name)

    print("\n" + "=" * 70)
    print(f"Folder: {folder}")
    print("   audio.wav | transcript.txt | summary.md")
    print("=" * 70 + "\n")
    print(summary)


# ============================================================================
# TRANSCRIBE
# ============================================================================

def _transcribe_groq(audio_path: pathlib.Path) -> str:
    """Hosted transcription via Groq Whisper-large-v3-turbo. Fast + cheap."""
    print(f"Transcribing {audio_path.name} via Groq Whisper-large-v3-turbo...")
    with open(audio_path, "rb") as f:
        resp = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files={"file": (audio_path.name, f, "audio/wav")},
            data={"model": "whisper-large-v3-turbo", "response_format": "text"},
            timeout=600,
        )
    if resp.status_code != 200:
        raise RuntimeError(f"Groq returned {resp.status_code}: {resp.text}")
    return resp.text.strip()


def _transcribe_local(audio_path: pathlib.Path) -> str:
    """Local Whisper via `python3 -m whisper`. No PATH dependency, no API key."""
    check = subprocess.run(
        [sys.executable, "-c", "import whisper"], capture_output=True
    )
    if check.returncode != 0:
        print("ERROR: openai-whisper package not importable from this Python.")
        print(f"Install it for THIS interpreter: {sys.executable} -m pip install -U openai-whisper")
        sys.exit(1)

    out_dir = audio_path.parent
    print(f"Transcribing {audio_path.name} via local Whisper (model: base)...")
    print("    First run downloads the model (~140 MB). Subsequent runs are faster.")
    result = subprocess.run(
        [
            sys.executable, "-m", "whisper", str(audio_path),
            "--model", "base",
            "--language", "en",
            "--output_format", "txt",
            "--output_dir", str(out_dir),
            "--fp16", "False",
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: whisper failed:\n{result.stderr}")
        sys.exit(1)

    txt_path = out_dir / (audio_path.stem + ".txt")
    if not txt_path.exists():
        print(f"ERROR: expected transcript at {txt_path}, not found.")
        sys.exit(1)
    return txt_path.read_text(encoding="utf-8").strip()


def transcribe_audio(audio_path: pathlib.Path, out_path: pathlib.Path) -> str:
    """Prefer Groq if GROQ_API_KEY set, else local Whisper."""
    if GROQ_API_KEY:
        try:
            transcript = _transcribe_groq(audio_path)
        except Exception as e:
            print(f"WARNING: Groq failed ({e}); falling back to local Whisper.")
            transcript = _transcribe_local(audio_path)
    else:
        transcript = _transcribe_local(audio_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(transcript, encoding="utf-8")
    print(f"Transcript saved: {out_path} ({len(transcript)} chars)")
    return transcript


# ============================================================================
# SUMMARIZE
# ============================================================================

def summarize_transcript(transcript: str, out_path: pathlib.Path, meeting_name: str) -> str:
    today = datetime.date.today().isoformat()
    user_prompt = (
        f"Meeting name: {meeting_name}\n"
        f"Date: {today}\n\n"
        f"Transcript:\n---\n{transcript}\n---\n\n"
        "Write the structured summary as instructed."
    )

    print("\nGenerating summary (premium tier)...")
    summary = complete(
        user_prompt,
        system=SUMMARY_SYSTEM_PROMPT,
        tier="premium",
        max_tokens=3000,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(summary, encoding="utf-8")
    print(f"Summary saved: {out_path}")
    return summary


# ============================================================================
# CLI
# ============================================================================

def cmd_transcribe_manual(audio_arg: str) -> None:
    audio_path = pathlib.Path(audio_arg).resolve()
    out_path = audio_path.parent / "transcript.txt"
    transcribe_audio(audio_path, out_path)


def cmd_summarize_manual(transcript_arg: str) -> None:
    transcript_path = pathlib.Path(transcript_arg).resolve()
    transcript = transcript_path.read_text(encoding="utf-8")
    out_path = transcript_path.parent / "summary.md"
    meeting_name = transcript_path.parent.name
    summary = summarize_transcript(transcript, out_path, meeting_name)
    print("\n" + "=" * 70)
    print(summary)
    print("=" * 70)


USAGE = """Usage:
    python3 tools/meeting_listener.py start <meeting-name>
    python3 tools/meeting_listener.py stop
    python3 tools/meeting_listener.py status
    python3 tools/meeting_listener.py transcribe <path-to-audio>
    python3 tools/meeting_listener.py summarize <path-to-transcript>
"""


def main():
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    mode = sys.argv[1].lower()

    if mode == "start":
        if len(sys.argv) < 3:
            print("ERROR: start requires a meeting name.\n")
            print(USAGE)
            sys.exit(1)
        cmd_start(" ".join(sys.argv[2:]))
    elif mode == "stop":
        cmd_stop()
    elif mode == "status":
        cmd_status()
    elif mode == "transcribe":
        if len(sys.argv) < 3:
            print(USAGE)
            sys.exit(1)
        cmd_transcribe_manual(sys.argv[2])
    elif mode == "summarize":
        if len(sys.argv) < 3:
            print(USAGE)
            sys.exit(1)
        cmd_summarize_manual(sys.argv[2])
    else:
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
