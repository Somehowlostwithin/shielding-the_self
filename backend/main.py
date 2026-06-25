"""
Shielding the Shelf — backend API.

Run locally:
    pip install -r requirements.txt
    python seed.py        # populate demo products
    uvicorn main:app --reload --port 8000

Then in each frontend file (index.html, dashboard.html, report.html):
    USE_MOCK = false
    API_BASE = "http://localhost:8000"
"""

import os
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

import logic
import models
import schemas
from database import Base, engine, get_db

# create tables on startup if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shielding the Shelf API")

# ============================================================
# Admin auth — protects the dashboard's data endpoints.
# Set a real secret in Render: Dashboard -> your service -> Environment
# -> add ADMIN_KEY = <something only you and your team know>.
# Locally it falls back to "changeme123" so dev still works without setup —
# but ALWAYS set a real ADMIN_KEY on Render before sharing the dashboard URL.
# ============================================================
ADMIN_KEY = os.environ.get("ADMIN_KEY", "changeme123")


def verify_admin(x_admin_key: str = Header(None)):
    if not x_admin_key or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key.")


@app.on_event("startup")
def auto_seed_products():
    """
    Runs both seed.py (the small basic demo set, including the
    guaranteed-FAKE demo code SENS-FAKE-01) and seed_50.py (the full
    250-product catalog) on every startup. Both seed() functions are
    idempotent — safe to run on every deploy/restart, since they only
    insert products that don't already exist by qr_code_id. This keeps
    the database in sync with whatever's in these files with zero
    manual steps (important for Render, where the free plan has no
    shell access to run scripts by hand).
    """
    try:
        import seed as seed_basic_module
        import seed_50 as seed_50_module
        seed_basic_module.seed()
        seed_50_module.seed()
    except Exception as e:
        # Don't crash the whole app if seeding hiccups — log and continue.
        print(f"[startup seeding] skipped due to error: {e}")

# Wide-open CORS for hackathon/demo purposes — tighten this before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "shielding-the-shelf-api"}


# ============================================================
# POST /scan — the heart of the project
# ============================================================
@app.post("/scan", response_model=schemas.ScanResponse)
def scan_qr(payload: schemas.ScanRequest, db: Session = Depends(get_db)):
    product = (
        db.query(models.Product)
        .filter(models.Product.qr_code_id == payload.qr_code_id)
        .first()
    )
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Unknown QR code — this code isn't registered to any product.",
        )

    # log the scan first, so it counts toward this very evaluation
    new_scan = models.Scan(
        qr_code_id=payload.qr_code_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        city=payload.city,
    )
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)

    level, scan_count, unique_cities, trigger = logic.evaluate_anomaly(db, payload.qr_code_id)

    # only the hard FAKE level counts toward the "flagged" bucket in the brand chart —
    # WARNING/CAUTION are softer signals, not a confirmed counterfeit call yet
    new_scan.is_anomalous = (level == "FAKE")
    db.commit()

    if trigger == "multi_city":
        reason = (
            f"This code has now been scanned from {unique_cities} different cities — "
            f"a single genuine product cannot physically be in more than one place. "
            f"Likely a duplicated QR code."
        )
    elif trigger == "city_limit":
        reason = (
            f"Scanned {scan_count} times in the same city — beyond the "
            f"{logic.SAME_CITY_SCAN_LIMIT}-scan limit expected for a single genuine unit."
        )
    elif level == "CAUTION":
        reason = (
            f"This is the {scan_count}rd time this exact code has been scanned in this city. "
            f"One more scan will flag it as counterfeit — keep an eye on this product."
        )
    elif level == "WARNING":
        reason = (
            f"This is the {scan_count}nd time this exact code has been scanned. "
            f"Still within normal range, but worth watching."
        )
    else:
        reason = "Scan pattern is within normal range for a genuine product."

    return schemas.ScanResponse(
        status=level,
        product_name=product.product_name,
        brand=product.brand,
        batch_number=product.batch_number,
        reason=reason,
        scan_count=scan_count,
        unique_cities=unique_cities,
    )


# ============================================================
# GET /product/{qr_code_id}
# ============================================================
@app.get("/product/{qr_code_id}", response_model=schemas.ProductResponse)
def get_product(qr_code_id: str, db: Session = Depends(get_db)):
    product = (
        db.query(models.Product)
        .filter(models.Product.qr_code_id == qr_code_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    return schemas.ProductResponse(
        brand=product.brand,
        product_name=product.product_name,
        batch_number=product.batch_number,
    )


# ============================================================
# POST /report
# ============================================================
@app.post("/report", response_model=schemas.ReportResponse)
def report_shop(payload: schemas.ReportRequest, db: Session = Depends(get_db)):
    new_report = models.Report(
        qr_code_id=payload.qr_code_id,
        shop_name=payload.shop_name,
        shop_city=payload.shop_city,
        latitude=payload.latitude,
        longitude=payload.longitude,
        notes=payload.notes,
    )
    db.add(new_report)
    db.commit()

    count = (
        db.query(models.Report)
        .filter(
            func.lower(models.Report.shop_name) == payload.shop_name.lower(),
            func.lower(models.Report.shop_city) == payload.shop_city.lower(),
        )
        .count()
    )

    status = "escalated" if count >= logic.REPORT_ESCALATION_THRESHOLD else "logged"
    return schemas.ReportResponse(status=status, report_count=count)


# ============================================================
# GET /anomalies — flagged QR codes, for the dashboard table
# ============================================================
@app.get("/anomalies", response_model=list[schemas.AnomalyItem])
def get_anomalies(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    all_codes = db.query(models.Scan.qr_code_id).distinct().all()

    results = []
    for (qr_code_id,) in all_codes:
        level, scan_count, unique_cities, trigger = logic.evaluate_anomaly(db, qr_code_id)
        if level == "SAFE":
            continue

        product = (
            db.query(models.Product)
            .filter(models.Product.qr_code_id == qr_code_id)
            .first()
        )
        latest_scan = (
            db.query(models.Scan)
            .filter(models.Scan.qr_code_id == qr_code_id)
            .order_by(models.Scan.timestamp.desc())
            .first()
        )

        report_groups = (
            db.query(models.Report.shop_name, models.Report.shop_city, func.count(models.Report.id))
            .filter(models.Report.qr_code_id == qr_code_id)
            .group_by(models.Report.shop_name, models.Report.shop_city)
            .all()
        )
        escalated = any(c >= logic.REPORT_ESCALATION_THRESHOLD for _, _, c in report_groups)

        results.append(
            schemas.AnomalyItem(
                qr_code_id=qr_code_id,
                brand=product.brand if product else "Unknown",
                scan_count=scan_count,
                unique_cities=unique_cities,
                flagged_at=latest_scan.timestamp if latest_scan else datetime.utcnow(),
                level=level,
                escalated=escalated,
            )
        )

    results.sort(key=lambda r: r.scan_count, reverse=True)
    return results


# ============================================================
# GET /hotzones — aggregated reports per shop, for the map
# ============================================================
@app.get("/hotzones", response_model=list[schemas.HotZoneItem])
def get_hotzones(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    rows = (
        db.query(
            models.Report.shop_name,
            models.Report.shop_city,
            func.avg(models.Report.latitude),
            func.avg(models.Report.longitude),
            func.count(models.Report.id),
        )
        .group_by(models.Report.shop_name, models.Report.shop_city)
        .all()
    )

    return [
        schemas.HotZoneItem(
            shop_name=shop_name,
            city=shop_city,
            latitude=lat,
            longitude=lng,
            report_count=count,
            escalated=count >= logic.REPORT_ESCALATION_THRESHOLD,
        )
        for shop_name, shop_city, lat, lng, count in rows
    ]


# ============================================================
# GET /stats — summary numbers for the dashboard stat cards
# ============================================================
@app.get("/stats", response_model=schemas.StatsResponse)
def get_stats(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    total_scans = db.query(models.Scan).count()
    # only count true FAKE-level codes here — WARNING/CAUTION are softer
    # signals shown in the anomaly table, not confirmed counterfeits
    flagged_codes = len([a for a in get_anomalies(db) if a.level == "FAKE"])
    active_hot_zones = len([h for h in get_hotzones(db) if h.escalated])
    reports_filed = db.query(models.Report).count()

    return schemas.StatsResponse(
        total_scans=total_scans,
        flagged_codes=flagged_codes,
        active_hot_zones=active_hot_zones,
        reports_filed=reports_filed,
    )


# ============================================================
# GET /brand_volume — genuine vs flagged scans per brand, for the chart
# ============================================================
@app.get("/brand_volume", response_model=list[schemas.BrandVolumeItem])
def get_brand_volume(db: Session = Depends(get_db), _: None = Depends(verify_admin)):
    products = db.query(models.Product).all()
    totals = {}  # brand -> {"genuine": int, "flagged": int}

    for product in products:
        scans = db.query(models.Scan).filter(models.Scan.qr_code_id == product.qr_code_id).all()
        flagged = len([s for s in scans if s.is_anomalous])
        genuine = len(scans) - flagged

        bucket = totals.setdefault(product.brand, {"genuine": 0, "flagged": 0})
        bucket["genuine"] += genuine
        bucket["flagged"] += flagged

    return [
        schemas.BrandVolumeItem(brand=brand, genuine=counts["genuine"], flagged=counts["flagged"])
        for brand, counts in totals.items()
    ]


# ============================================================
# Serve the frontend (index.html, dashboard.html, report.html) from this
# SAME server, so the whole app — API + pages — is reachable through one
# single port/URL. This MUST be the last thing registered: StaticFiles
# mounted at "/" only catches paths that don't match an explicit route
# declared above it, so /scan, /report, /api/health etc. all keep working.
# ============================================================
from fastapi.staticfiles import StaticFiles

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
