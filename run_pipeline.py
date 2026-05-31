import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EVENTS_FILE = BASE_DIR / "data" / "events" / "events.jsonl"
EVENT_GENERATOR = BASE_DIR / "pipeline" / "event_generator.py"
LOAD_EVENTS = BASE_DIR / "pipeline" / "load_events_to_db.py"

PIPELINE_MAX_SECONDS = 300
EVENT_GENERATOR_TIMEOUT_SECONDS = 270


def run() -> int:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    start_time = time.time()

    if EVENTS_FILE.exists() and EVENTS_FILE.stat().st_size > 0:
        print(f"Events file already exists at {EVENTS_FILE}; skipping generation.")
    else:
        print("Running event generator...")
        try:
            gen_proc = subprocess.run(
                [sys.executable, str(EVENT_GENERATOR)],
                timeout=EVENT_GENERATOR_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            print(
                f"Event generator exceeded {EVENT_GENERATOR_TIMEOUT_SECONDS} seconds and was terminated."
            )
            return 1

        if gen_proc.returncode != 0:
            print("Event generator exited with code", gen_proc.returncode)
            return gen_proc.returncode

    if not EVENTS_FILE.exists() or EVENTS_FILE.stat().st_size == 0:
        print(f"No events file found at {EVENTS_FILE}. Nothing to load.")
        return 1

    elapsed = time.time() - start_time
    remaining_time = PIPELINE_MAX_SECONDS - elapsed
    if remaining_time <= 0:
        print("Pipeline exceeded 5-minute limit before DB load.")
        return 1

    print("Loading events into DB...")
    try:
        load_proc = subprocess.run(
            [sys.executable, str(LOAD_EVENTS)],
            cwd=str(BASE_DIR),
            capture_output=True,
            text=True,
            timeout=remaining_time,
        )
    except subprocess.TimeoutExpired:
        print("Event loader exceeded remaining time and was terminated.")
        return 1

    if load_proc.stdout:
        print(load_proc.stdout.strip())
    if load_proc.stderr:
        print(load_proc.stderr.strip())
    if load_proc.returncode != 0:
        print("Loader exited with code", load_proc.returncode)
        return load_proc.returncode

    total_elapsed = time.time() - start_time
    print(f"Pipeline completed in {total_elapsed:.1f}s.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
