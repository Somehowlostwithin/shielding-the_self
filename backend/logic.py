"""
The heart of the project: deciding whether a QR code's scan pattern is
physically plausible for one genuine product, or a sign of mass duplication.

Rule (all-time, no rolling window):
  - A genuine product can be scanned a few times by curious customers in
    ONE city/shop — up to SAME_CITY_SCAN_LIMIT scans is treated as normal.
    The next scan past that limit, still in that one city, is flagged.
  - The moment the SAME QR code is ever scanned from a SECOND distinct
    city, that's immediate proof of duplication — one physical bottle
    cannot be in two cities. Flagged instantly, regardless of count.
"""

from sqlalchemy.orm import Session

import models

SAME_CITY_SCAN_LIMIT = 3
REPORT_ESCALATION_THRESHOLD = 3


def get_all_scans(db: Session, qr_code_id: str):
    """Every scan ever logged for this QR code — no time window."""
    return db.query(models.Scan).filter(models.Scan.qr_code_id == qr_code_id).all()


def evaluate_anomaly(db: Session, qr_code_id: str):
    """
    Returns (is_anomalous, scan_count, unique_cities, trigger) for a given
    QR code, based on ALL scans it has ever received.

    trigger is one of: None, "multi_city", "city_limit"
    """
    scans = get_all_scans(db, qr_code_id)
    scan_count = len(scans)

    # normalize city names for comparison so "Delhi" and "delhi" count as one
    normalized_cities = {s.city.strip().lower() for s in scans if s.city and s.city.strip()}
    unique_cities = len(normalized_cities)

    if unique_cities >= 2:
        return True, scan_count, unique_cities, "multi_city"

    if scan_count > SAME_CITY_SCAN_LIMIT:
        return True, scan_count, unique_cities, "city_limit"

    return False, scan_count, unique_cities, None
