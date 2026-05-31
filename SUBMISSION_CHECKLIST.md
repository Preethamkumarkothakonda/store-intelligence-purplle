# Final Submission Checklist

Use this checklist before submitting the Store Intelligence project for the Purplle Tech Challenge.

---

## Repository

- [ ] Repository is public (or shared with evaluators)
- [ ] `README.md` is complete and accurate
- [ ] `DESIGN.md` documents system architecture
- [ ] `CHOICES.md` explains technology decisions
- [ ] `DEMO_SCRIPT.md` is ready for video presentation
- [ ] `docs/ARCHITECTURE.md` contains Mermaid diagrams
- [ ] `.gitignore` excludes videos, venv, and bytecode
- [ ] No secrets, API keys, or credentials committed

---

## Required Artifacts (Committed)

- [ ] `store.db` — pre-generated SQLite database with events
- [ ] `data/events/events.jsonl` — generated visitor events
- [ ] `data/sales/store_sales.csv` — POS sales data
- [ ] `Dockerfile` — API-only container definition
- [ ] `docker-compose.yml` — single-service deployment
- [ ] `requirements-api.txt` — pinned API dependencies
- [ ] `requirements-pipeline.txt` — ML pipeline dependencies

---

## Artifacts NOT Committed (Excluded)

- [ ] `data/videos/` — CCTV footage excluded via `.gitignore`
- [ ] `*.mp4` — video files excluded
- [ ] `venv/` / `.venv/` — local Python environments excluded
- [ ] `__pycache__/` — bytecode excluded

---

## Docker Verification

- [ ] Docker Desktop is installed and running
- [ ] `docker compose up --build` completes without errors
- [ ] Container starts in under 5 minutes
- [ ] API responds on port 8000

```bash
docker compose up --build
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

---

## API Endpoint Verification

Run all endpoints and confirm HTTP 200 responses:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/stores/STORE_001/metrics
curl http://localhost:8000/stores/STORE_001/heatmap
curl http://localhost:8000/stores/STORE_001/anomalies
curl http://localhost:8000/stores/STORE_001/funnel
curl http://localhost:8000/stores/ST1008/sales
```

| Endpoint | Expected |
|---|---|
| `/health` | `{"status":"healthy"}` |
| `/stores/STORE_001/metrics` | `unique_visitors` > 0 |
| `/stores/STORE_001/heatmap` | Zone counts present |
| `/stores/STORE_001/anomalies` | Valid JSON (may be empty) |
| `/stores/STORE_001/funnel` | `conversion_rate` present |
| `/stores/ST1008/sales` | `revenue` > 0 |

- [ ] All 6 endpoints return valid JSON
- [ ] Swagger UI accessible at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Testing Verification

- [ ] Run test suite locally and ensure all tests pass:

```bash
# Run pytest in the virtual environment
.venv\Scripts\pytest
```

- [ ] All 4 core API tests pass successfully:
  - `test_health` (HTTP 200)
  - `test_metrics` (HTTP 200, contains store_id)
  - `test_funnel` (HTTP 200, contains visitors)
  - `test_sales` (HTTP 200, contains revenue)

---

## Pipeline Verification (Optional — Local Only)

- [ ] Python 3.9+ installed
- [ ] Pipeline dependencies installed: `pip install -r requirements-pipeline.txt`
- [ ] `python run_pipeline.py` completes in under 5 minutes
- [ ] Skips generation when `events.jsonl` already exists
- [ ] Loads events into `store.db` successfully

---

## Code Quality

- [ ] No hardcoded secrets or credentials
- [ ] Application code unchanged since feature completion
- [ ] FastAPI auto-docs reflect all endpoints
- [ ] Docker image does NOT include torch, opencv, or ultralytics

---

## Demo Video (If Required)

- [ ] 2-minute demo recorded using `DEMO_SCRIPT.md`
- [ ] Shows architecture overview
- [ ] Demonstrates at least 3 API endpoints live
- [ ] Shows `docker compose up --build` working
- [ ] Audio is clear; terminal text is readable

---

## Fresh Clone Test (Critical)

Simulate the evaluator experience on a clean machine:

```bash
git clone <repository-url>
cd store-intelligence
docker compose up --build
curl http://localhost:8000/health
curl http://localhost:8000/stores/STORE_001/metrics
curl http://localhost:8000/stores/ST1008/sales
```

- [ ] Clone → Docker → API works without manual setup
- [ ] No pipeline or video files required for evaluation
- [ ] Total time from clone to working API is under 5 minutes

---

## Submission Package

- [ ] GitHub repository URL ready
- [ ] Demo video link ready (if required)
- [ ] Team member names and roles documented
- [ ] Any setup notes for evaluators included in README

---

## Quick Reference

| Action | Command |
|---|---|
| Start API (Docker) | `docker compose up --build` |
| Start API (local) | `uvicorn app.main:app --reload --port 8000` |
| Run pipeline | `python run_pipeline.py` |
| API docs | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Health check | [http://localhost:8000/health](http://localhost:8000/health) |

---

**Status:** ☐ Ready for submission

**Date verified:** _______________

**Verified by:** _______________
