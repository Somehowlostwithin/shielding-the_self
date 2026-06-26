# 🛡️ Shielding The Shelf

### Crowd-Sourced Counterfeit Product Detection using QR-Based Anomaly Analysis

> A web-based surveillance platform that identifies counterfeit consumer products by analyzing QR scan behaviour across locations and time, enabling real-time detection and community-driven reporting.

## Overview

Counterfeit consumer goods have evolved beyond poor-quality imitations. Modern counterfeiters replicate packaging, branding, batch numbers, expiry dates, and even genuine QR codes, making traditional visual verification ineffective.

Shielding The Shelf addresses this challenge by shifting authentication from **static QR verification** to **behavioural anomaly detection**. Rather than validating whether a QR code exists, the system evaluates how that QR code behaves after it has been scanned by users.

By combining crowd-sourced scan telemetry with geographic analysis and customer reports, the platform identifies suspicious product movement patterns that are highly unlikely for genuine products.

## Problem Statement

Conventional product verification systems rely on static QR codes that simply redirect users to a manufacturer's website.

This approach fails because counterfeiters often duplicate a genuine QR code across thousands of fake products. Every counterfeit product therefore appears authentic despite sharing the same identifier.

As a result,

- Consumers unknowingly purchase counterfeit products.
- Manufacturers suffer financial and reputational losses.
- Authorities receive counterfeit reports only after significant market damage.

---

## Proposed Solution

Shielding The Shelf introduces a behavioural verification system.

Every product scan contributes anonymous telemetry including:

- QR Code Identifier
- Scan Timestamp
- Geographic Location
- Scan Frequency

The backend continuously evaluates these records to detect abnormal scanning behaviour.

For example,

> If the same QR code is scanned from multiple geographically distant locations within a short period of time, the system flags the product as potentially counterfeit and allows customers to report the source of purchase.

Repeated reports against the same retailer automatically classify that location as a **Hot Zone**, allowing administrators to monitor counterfeit distribution patterns in real time.

---

# Key Features

### QR Code Verification

- Product authenticity verification
- Manual QR code entry
- Behaviour-based counterfeit detection
- Product information retrieval

---

### Behavioural Anomaly Detection

Detection based on:

- Scan frequency
- Geographic distribution
- Duplicate QR activity
- Community scan telemetry

---

### Community Reporting

Customers can report suspicious retailers by submitting:

- QR Code
- Shop Name
- City
- GPS Coordinates
- Additional observations

---

### Administrative Surveillance Dashboard

The dashboard provides administrators with:

- Live scan statistics
- Counterfeit detection metrics
- Geographic hot-zone visualization
- Customer report analytics
- Brand-wise scan distribution
- Real-time anomaly monitoring


# Project Structure

```
backend/
│
├── main.py
├── database.py
├── models.py
├── schemas.py
├── logic.py
├── seed.py
├── requirements.txt
├── Procfile
└── render.yaml

index.html
dashboard.html
report.html
README.md
```

# Future Scope

- Dynamic time-window anomaly analysis
- Brand-specific detection thresholds
- Manufacturer analytics portal
- Counterfeit trend forecasting
- Mobile application support
- Advanced reporting and visualization

---

# Team

Developed as a hackathon project to demonstrate how crowd-sourced behavioural analytics can strengthen counterfeit product detection and improve consumer trust.
