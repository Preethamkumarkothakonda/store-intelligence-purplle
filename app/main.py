from fastapi import FastAPI
from sqlalchemy.orm import Session
import pandas as pd
from app.logger import logger
from app.database import SessionLocal
from app.models import Event
from app.schemas import EventCreate

app = FastAPI()


@app.on_event("startup")
def on_startup():
    logger.info("Store Intelligence API started")


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "healthy"}


# -----------------------------
# EVENT INGESTION
# -----------------------------
@app.post("/events/ingest")
def ingest_event(event: EventCreate):
    logger.info(f"Ingesting event {event.event_id}")

    db: Session = SessionLocal()

    existing = (
        db.query(Event)
        .filter(Event.event_id == event.event_id)
        .first()
    )

    if existing:
        db.close()
        return {"status": "duplicate_event"}

    db_event = Event(
        event_id=event.event_id,
        store_id=event.store_id,
        visitor_id=event.visitor_id,
        camera_id=event.camera_id,
        event_type=event.event_type,
        timestamp=event.timestamp,
        zone_id=event.zone_id,
        dwell_seconds=event.dwell_seconds,
        is_staff=event.is_staff,
        confidence=event.confidence,
    )

    db.add(db_event)
    db.commit()
    db.close()

    return {"status": "success"}


# -----------------------------
# STORE METRICS
# -----------------------------
# -----------------------------
# STORE METRICS
# -----------------------------
@app.get("/stores/{store_id}/metrics")
def get_metrics(store_id: str):
    logger.info(f"Metrics requested for {store_id}")

    db = SessionLocal()

    events = (
        db.query(Event)
        .filter(Event.store_id == store_id)
        .all()
    )

    customer_events = [
        e for e in events
        if not e.is_staff
    ]

    unique_visitors = len(
        set(e.visitor_id for e in customer_events)
    )

    avg_dwell = 0

    if customer_events:
        avg_dwell = (
            sum(e.dwell_seconds for e in customer_events)
            / len(customer_events)
        )

    staff_count = len(
        set(
            e.visitor_id
            for e in events
            if e.is_staff
        )
    )

    db.close()

    return {
        "store_id": store_id,
        "unique_visitors": unique_visitors,
        "average_dwell_time": round(avg_dwell, 2),
        "staff_count": staff_count,
        "total_events": len(events)
    }


# -----------------------------
# HEATMAP
# -----------------------------
@app.get("/stores/{store_id}/heatmap")
def get_heatmap(store_id: str):
    logger.info(f"Heatmap requested for {store_id}")

    db = SessionLocal()

    events = (
        db.query(Event)
        .filter(Event.store_id == store_id)
        .all()
    )

    zone_counts = {}

    for event in events:

        zone = event.zone_id

        if zone not in zone_counts:
            zone_counts[zone] = 0

        zone_counts[zone] += 1

    db.close()

    return {
        "store_id": store_id,
        "heatmap": zone_counts
    }
@app.get("/stores/{store_id}/anomalies")
def get_anomalies(store_id: str):
    logger.info(f"Anomalies requested for {store_id}")

    db = SessionLocal()

    events = (
        db.query(Event)
        .filter(Event.store_id == store_id)
        .all()
    )

    anomalies = []

    for event in events:

        if event.dwell_seconds > 25:

            anomalies.append({
                "visitor_id": event.visitor_id,
                "type": "LONG_DWELL_TIME",
                "zone": event.zone_id,
                "dwell_seconds": event.dwell_seconds
            })

    db.close()

    return {
        "store_id": store_id,
        "anomalies": anomalies,
        "count": len(anomalies)
    }
@app.get("/stores/{store_id}/funnel")
def get_funnel(store_id: str):
    logger.info(f"Funnel requested for {store_id}")

    db = SessionLocal()

    events = (
        db.query(Event)
        .filter(Event.store_id == store_id)
        .all()
    )

    # Unique visitors
    visitors = len(
        set(e.visitor_id for e in events if not e.is_staff)
    )

    # Engaged visitors
    engaged = len(
        set(
            e.visitor_id
            for e in events
            if not e.is_staff and e.dwell_seconds >= 10
        )
    )

    # Approximate billing visitors
    billing = len(
        set(
            e.visitor_id
            for e in events
            if not e.is_staff and (
                e.camera_id == "CAM 5" or
                e.zone_id == "BILLING"
            )
        )
    )

    conversion_rate = 0

    if visitors > 0:
        conversion_rate = round(
            (billing / visitors) * 100,
            2
        )

    db.close()

    return {
        "store_id": store_id,
        "visitors": visitors,
        "engaged": engaged,
        "billing": billing,
        "conversion_rate": conversion_rate
    }


@app.get("/stores/{store_id}/sales")
def get_sales(store_id: str):
    logger.info(f"Sales requested for {store_id}")

    csv_path = "data/sales/store_sales.csv"

    df = pd.read_csv(csv_path)

    store_df = df[df["store_id"] == store_id]

    transactions = store_df["invoice_number"].nunique()

    revenue = round(
        store_df["total_amount"].sum(),
        2
    )

    avg_order_value = 0

    if transactions > 0:
        avg_order_value = round(
            revenue / transactions,
            2
        )

    top_products = (
        store_df["product_name"]
        .value_counts()
        .head(5)
        .index
        .tolist()
    )

    return {
        "store_id": store_id,
        "transactions": int(transactions),
        "revenue": revenue,
        "average_order_value": avg_order_value,
        "top_products": top_products
    }