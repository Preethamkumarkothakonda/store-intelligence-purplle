import json
import sys
from pathlib import Path

from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.database import SessionLocal, engine
from app.models import Base, Event

EVENT_PATH = BASE_DIR / "data" / "events" / "events.jsonl"
DEFAULT_STORE_ID = "STORE_001"
BATCH_SIZE = 500

if not EVENT_PATH.exists() or EVENT_PATH.stat().st_size == 0:
    print(f"Events file not found or empty: {EVENT_PATH}. Nothing to load.")
    sys.exit(0)

Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()
count = 0
skipped = 0

try:
    with open(EVENT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            event = json.loads(line)
            event_id = event.get("event_id")
            if not event_id:
                skipped += 1
                continue

            existing = (
                db.query(Event)
                .filter(Event.event_id == event_id)
                .first()
            )
            if existing:
                skipped += 1
                continue

            db.add(
                Event(
                    event_id=event_id,
                    store_id=event.get("store_id", DEFAULT_STORE_ID),
                    visitor_id=event.get("visitor_id"),
                    camera_id=event.get("camera_id"),
                    event_type=event.get("event_type"),
                    timestamp=event.get("timestamp"),
                    zone_id=event.get("zone_id"),
                    dwell_seconds=event.get("dwell_seconds", 0.0),
                    is_staff=event.get("is_staff", False),
                    confidence=event.get("confidence", 0.0),
                )
            )
            count += 1

            if count % BATCH_SIZE == 0:
                db.commit()

    db.commit()
finally:
    db.close()

print(f"{count} events loaded ({skipped} skipped as duplicates or invalid).")
