# Store Intelligence — Engineering Choices

This document explains the technology and architectural decisions made during the Purplle Tech Challenge hackathon, including tradeoffs accepted and the rationale behind each choice.

---

## Why YOLOv8n

**Choice:** YOLOv8 nano (`yolov8n.pt`) via the Ultralytics Python SDK.

**Rationale:**
- **Speed:** Nano is the smallest YOLOv8 variant — critical for CPU-only hackathon hardware
- **Accuracy:** Sufficient for person detection (COCO class 0) in fixed CCTV angles
- **Ecosystem:** Ultralytics provides unified APIs for detection, tracking, and model management
- **Zero-config tracking:** Built-in ByteTrack integration via `model.track()`

**Alternatives considered:**

| Option | Why not chosen |
|---|---|
| YOLOv8s/m/l | Too slow on CPU for 5-minute pipeline budget |
| Faster R-CNN | Heavier dependency chain, slower inference |
| MediaPipe | Less flexible for multi-person retail scenes |
| Custom model | No training data or time in hackathon scope |

---

## Why ByteTrack

**Choice:** ByteTrack tracker via Ultralytics (`tracker="bytetrack.yaml"`).

**Rationale:**
- **State-of-the-art MOT:** Strong performance on crowded scenes without appearance features
- **Low association threshold:** Recovers tracks through brief occlusions (common in retail)
- **Integrated:** No separate tracker library; works out-of-box with YOLOv8
- **Persistent IDs:** `persist=True` maintains track IDs across frames and videos

**Tradeoff:** Track IDs reset between pipeline runs. Production would require Re-ID across sessions and cameras.

---

## Why SQLite

**Choice:** SQLite file database (`store.db`) with SQLAlchemy ORM.

**Rationale:**
- **Zero infrastructure:** No database server to install or configure
- **Portable:** Single file ships inside Docker image for instant evaluation
- **Sufficient scale:** Handles thousands of events easily for hackathon demo
- **SQLAlchemy abstraction:** Easy migration path to PostgreSQL

**Alternatives considered:**

| Option | Why not chosen |
|---|---|
| PostgreSQL | Requires separate container; overkill for demo |
| MongoDB | Less natural fit for relational analytics queries |
| In-memory only | Data lost on restart; poor evaluator experience |
| JSON file queries | Slow aggregations; no indexing |

**Production upgrade:** PostgreSQL with read replicas and connection pooling.

---

## Why FastAPI

**Choice:** FastAPI + Uvicorn + Pydantic v2.

**Rationale:**
- **Auto OpenAPI docs:** `/docs` endpoint for instant API exploration by evaluators
- **Type safety:** Pydantic schemas validate ingestion payloads
- **Performance:** Async-capable ASGI framework, among the fastest Python options
- **Minimal boilerplate:** Route definitions are concise and readable

**Alternatives considered:**

| Option | Why not chosen |
|---|---|
| Flask | No automatic schema validation or OpenAPI |
| Django REST | Heavy framework for a focused analytics API |
| Node.js/Express | Team strength and ML ecosystem alignment with Python |

---

## Why Docker

**Choice:** Single-service Docker Compose with API-only slim image.

**Rationale:**
- **Reproducibility:** Evaluators get identical runtime regardless of local Python setup
- **Isolation:** API dependencies pinned in `requirements-api.txt`
- **Fast startup:** No ML libraries in image → build and start in under 2 minutes
- **Industry standard:** Demonstrates deployment readiness expected in production roles

**Design decision:** Docker runs **only FastAPI**, not the ML pipeline. This is intentional — see next section.

---

## Why Pre-Generated Database for Evaluation

**Choice:** Commit `store.db` and `data/events/events.jsonl` to the repository; Docker serves from baked-in artifacts.

**Rationale:**

| Problem | Solution |
|---|---|
| ML pipeline takes 5+ minutes on CPU | Pre-generate events locally once |
| Docker image with torch/opencv is 2+ GB | API image stays ~200 MB |
| Evaluators may not have GPU or videos | Instant API demo with real data |
| Hackathon time limit | `docker compose up` → working APIs in minutes |

**Workflow:**
```
Developer:  python run_pipeline.py  →  generates store.db (one-time, local)
Evaluator:  docker compose up       →  instant API with pre-built data
```

This mirrors production where batch inference and online serving are separate services.

---

## Engineering Tradeoffs

| Tradeoff | Decision | Impact |
|---|---|---|
| Accuracy vs. speed | `FRAME_SKIP=10` | 10× faster; may miss short visits |
| Coverage vs. time | CAM1–CAM3 only | Skips CAM4/CAM5 to meet 5-min budget |
| Zone precision | Camera-level zones | Simple but not pixel-accurate |
| Real-time vs. batch | Batch MP4 processing | No live RTSP; simpler to build |
| Staff detection | Not implemented | All visitors treated as customers |
| Event deduplication | One event per track ID | Prevents inflation; misses re-visits |
| Sales integration | Static CSV | No live POS; sufficient for demo |

---

## Hardware Constraints

The pipeline was designed and tested under these constraints:

| Constraint | Mitigation |
|---|---|
| CPU-only inference | YOLOv8n + frame skip |
| 5-minute pipeline deadline | Max 1000 frames/video, 3 cameras |
| Limited RAM | Nano model (~6 MB weights) |
| No GPU in Docker eval | Pre-generated DB eliminates inference in container |
| Windows development | Path handling via `pathlib`; Docker for Linux deployment |

---

## Future Production Improvements

### Computer Vision
- GPU inference with TensorRT or ONNX Runtime
- Polygon ROI zone mapping per camera
- Staff uniform classification model
- Multi-camera person Re-ID

### Data Platform
- Kafka for real-time event streaming
- PostgreSQL / TimescaleDB for time-series analytics
- dbt models for funnel and cohort analysis
- Data lake for raw video archival (S3 + lifecycle policies)

### API & Platform
- JWT authentication and multi-tenant store isolation
- Rate limiting and API versioning
- Redis caching for hot analytics queries
- Celery workers for async aggregation jobs

### DevOps
- CI/CD pipeline (GitHub Actions)
- Separate Docker images for pipeline worker and API
- Kubernetes deployment with horizontal pod autoscaling
- Prometheus + Grafana observability stack

### Product
- Real-time dashboard for store managers
- Alerting on anomaly detection (long dwell, crowd density)
- A/B testing integration for in-store layout changes
- POS system integration for true conversion tracking
