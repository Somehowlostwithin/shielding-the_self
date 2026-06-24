# Shielding — Fake Product Detection via QR Scanning

A web app that lets users scan product QR codes to verify authenticity, flag counterfeit/fake products, and report suspicious shops. Built for [hackathon name / event — add if applicable].

## Features

- **QR Code Scanning** — Scan a product's QR code to check if it's genuine or flagged as fake
- **Product Lookup** — Retrieve product details by QR code ID
- **Anomaly Detection** — Identify unusual scan patterns that may indicate counterfeit activity
- **Hot Zones** — Track geographic areas with high concentrations of fake product reports
- **Shop Reporting** — Allow users to report shops selling suspicious/fake products
- **Stats Dashboard** — View total scans, flagged codes, active hot zones, and reports filed
- **Brand Volume Tracking** — Monitor scan volume per brand

## Tech Stack

- **Backend:** FastAPI (Python), SQLAlchemy, PostgreSQL
- **Frontend:** HTML/CSS/JS (Dashboard, Scan, Report pages)
- **Deployment:** Render (Web Service + PostgreSQL)

## Project Structure
