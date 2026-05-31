# Architecture Diagram

Standalone reference for the Store Intelligence data pipeline.

```mermaid
flowchart LR
    A[CCTV Videos] --> B[YOLOv8]
    B --> C[ByteTrack]
    C --> D[Event Generator]
    D --> E[events.jsonl]
    E --> F[SQLite]
    F --> G[FastAPI]
    G --> H[Analytics APIs]
```

## Stage Descriptions

| Stage | Component | Technology |
|---|---|---|
| Input | CCTV Videos | MP4 files (CAM1, CAM2, CAM3) |
| Detection | YOLOv8 | YOLOv8n person detection |
| Tracking | ByteTrack | Multi-object identity tracking |
| Events | Event Generator | ZONE_DWELL event creation |
| Storage | events.jsonl | Append-only JSON Lines file |
| Database | SQLite | Relational event store (`store.db`) |
| API | FastAPI | REST analytics service |
| Output | Analytics APIs | Metrics, heatmap, funnel, sales |

## Deployment Split

```mermaid
flowchart TB
    subgraph local ["Local Machine"]
        P[run_pipeline.py]
        P --> EG[event_generator.py]
        EG --> JSONL[events.jsonl]
        JSONL --> LOAD[load_events_to_db.py]
        LOAD --> DB[(store.db)]
    end

    subgraph docker ["Docker Container"]
        DB2[(store.db)] --> API[FastAPI :8000]
        API --> EP[Analytics Endpoints]
    end

    DB -.->|committed to repo| DB2
```

The offline pipeline runs locally. Docker serves the pre-built database through FastAPI only.
