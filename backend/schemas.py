from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ---------- /scan ----------
class ScanRequest(BaseModel):
    qr_code_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None


class ScanResponse(BaseModel):
    status: str  # "SAFE" | "FAKE"
    product_name: Optional[str] = None
    brand: Optional[str] = None
    batch_number: Optional[str] = None
    reason: str
    scan_count: int
    unique_cities: int


# ---------- /product/{qr_code_id} ----------
class ProductResponse(BaseModel):
    brand: str
    product_name: str
    batch_number: Optional[str] = None


# ---------- /report ----------
class ReportRequest(BaseModel):
    qr_code_id: str
    shop_name: str
    shop_city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class ReportResponse(BaseModel):
    status: str  # "logged" | "escalated"
    report_count: int


# ---------- /anomalies ----------
class AnomalyItem(BaseModel):
    qr_code_id: str
    brand: str
    scan_count: int
    unique_cities: int
    flagged_at: datetime
    escalated: bool


# ---------- /stats ----------
class StatsResponse(BaseModel):
    total_scans: int
    flagged_codes: int
    active_hot_zones: int
    reports_filed: int


# ---------- /hotzones ----------
class HotZoneItem(BaseModel):
    shop_name: str
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    report_count: int
    escalated: bool


# ---------- /brand_volume ----------
class BrandVolumeItem(BaseModel):
    brand: str
    genuine: int
    flagged: int
