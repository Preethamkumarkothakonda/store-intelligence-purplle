from pathlib import Path
from ultralytics import YOLO
import cv2
import json
from datetime import datetime
import sys
import os
import time


# Base project directory (two levels up from this file: project_root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Model path (try project root then pipeline folder)
model_path = BASE_DIR / "yolov8n.pt"
if not model_path.exists():
    alt = Path(__file__).resolve().parent / "yolov8n.pt"
    if alt.exists():
        model_path = alt

model_spec = str(model_path) if model_path.exists() else "yolov8n.pt"

# Load YOLO model
model = YOLO(model_spec)

# Directories
VIDEO_DIR = BASE_DIR / "data" / "videos"
EVENT_DIR = BASE_DIR / "data" / "events"
EVENT_DIR.mkdir(parents=True, exist_ok=True)
EVENT_PATH = EVENT_DIR / "events.jsonl"

# Debug info
print(f"BASE_DIR: {BASE_DIR}")
print(f"Model path: {model_spec}")
print(f"Video dir: {VIDEO_DIR}")

ALLOWED_CAMERAS = {"CAM1", "CAM2", "CAM3", "CAM 1", "CAM 2", "CAM 3"}

# Find videos automatically; only CAM1-CAM3 (skip CAM4 and CAM5)
videos = sorted(VIDEO_DIR.glob("*.mp4"))
videos = [v for v in videos if v.stem in ALLOWED_CAMERAS]
if not videos:
    print("No .mp4 videos found for CAM1-CAM3 in:", VIDEO_DIR)
    sys.exit(0)

print(f"Found {len(videos)} videos (CAM1-CAM3)")

# Tracking state shared across videos
first_seen_frame = {}
emitted_visitors = set()

# Frame skip for performance (process every Nth frame)
FRAME_SKIP = 10
# Maximum frames to process per video (prevents long videos from running forever)
MAX_FRAMES_PER_VIDEO = 1000

# Maximum runtime for this generator (seconds)
PIPELINE_MAX_SECONDS = 300

# Processing statistics
total_frames = 0
processed_frames = 0

start_time = time.time()
deadline = start_time + PIPELINE_MAX_SECONDS
stop_processing = False

print("Starting event generation...")

for video_path in videos:

    print(f"\nProcessing video: {video_path}")
    print(f"Video exists: {video_path.exists()}")

    cap = cv2.VideoCapture(str(video_path))
    print(f"Video opened: {cap.isOpened()}")
    try:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    except Exception:
        frame_count = 0
    print("Frame count:", frame_count)

    # FPS fallback
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    frame_number = 0

    while cap.isOpened():
        if time.time() >= deadline:
            print("Reached 5-minute limit; stopping event generation.")
            stop_processing = True
            break

        success, frame = cap.read()
        if not success:
            break

        frame_number += 1
        total_frames += 1

        # Stop processing this video after a maximum number of frames
        if frame_number >= MAX_FRAMES_PER_VIDEO:
            print(f"Reached max frames ({MAX_FRAMES_PER_VIDEO}) for {video_path.stem}; moving to next video.")
            break

        # Skip frames to speed up processing while keeping frame numbering for dwell time
        if frame_number % FRAME_SKIP != 0:
            continue
        processed_frames += 1

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[0],
            verbose=False
        )

        annotated_frame = results[0].plot()

        if results[0].boxes.id is not None:

            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)

            for box, track_id in zip(boxes, track_ids):

                # Save first frame seen
                if track_id not in first_seen_frame:
                    first_seen_frame[track_id] = frame_number

                # Already emitted event for this visitor
                if track_id in emitted_visitors:
                    continue

                # Calculate dwell time from frames
                dwell_seconds = (frame_number - first_seen_frame[track_id]) / fps

                # Generate dwell event after 10 seconds
                if dwell_seconds >= 10:
                    is_staff = False
                    visitor_id = f"VIS_{track_id}"

                    event = {
                        "event_id": f"EVT_{track_id}_{frame_number}",
                        "visitor_id": visitor_id,
                        "camera_id": video_path.stem,
                        "event_type": "ZONE_DWELL",
                        "timestamp": datetime.utcnow().isoformat(),
                        "zone_id": "SKINCARE",
                        "dwell_seconds": round(dwell_seconds, 2),
                        "is_staff": is_staff,
                        "confidence": 0.90,
                        "metadata": {"session_seq": 1},
                    }

                    print("Generated event:", event)

                    # Append event to file
                    with open(EVENT_PATH, "a", encoding="utf-8") as f:
                        f.write(json.dumps(event) + "\n")

                    emitted_visitors.add(track_id)

        # Only show window if explicitly requested (avoids issues in headless/docker)
        if os.environ.get("SHOW_VIDEO") == "1":
            cv2.imshow("Event Generation", annotated_frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    cap.release()

    if stop_processing:
        break

cv2.destroyAllWindows()

print("\nDone.")
print(f"Total unique visitors: {len(first_seen_frame)}")
print(f"Events generated: {len(emitted_visitors)}")
print(f"Event file written to: {EVENT_PATH}")
print("Event generation completed.")

end_time = time.time()
elapsed = end_time - start_time
print("\nProcessing statistics:")
print(f"  Total frames: {total_frames}")
print(f"  Processed frames: {processed_frames} (FRAME_SKIP={FRAME_SKIP})")
print(f"  Processing time (s): {elapsed:.2f}")