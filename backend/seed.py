"""
Populates the database with demo products so you have real QR codes to
print/test/scan during the hackathon demo.

Run once:
    python seed.py
"""

from database import Base, SessionLocal, engine
import models

Base.metadata.create_all(bind=engine)

DEMO_PRODUCTS = [
    {
        "qr_code_id": "SENS-0001",
        "brand": "Sensodyne",
        "product_name": "Sensodyne Rapid Relief Toothpaste",
        "batch_number": "B23A1",
    },
    {
        # deliberately kept around so judges can scan/type this for a guaranteed FAKE demo
        "qr_code_id": "SENS-FAKE-01",
        "brand": "Sensodyne",
        "product_name": "Sensodyne Rapid Relief Toothpaste",
        "batch_number": "B23A1",
    },
    {
        "qr_code_id": "AMUL-0001",
        "brand": "Amul",
        "product_name": "Amul Gold Milk 1L",
        "batch_number": "A45B2",
    },
    {
        "qr_code_id": "COLG-0001",
        "brand": "Colgate",
        "product_name": "Colgate Total Toothpaste",
        "batch_number": "C19D7",
    },
    {
        "qr_code_id": "DETT-0001",
        "brand": "Dettol",
        "product_name": "Dettol Antiseptic Liquid",
        "batch_number": "D88E3",
    },
    {
        "qr_code_id": "PARL-0001",
        "brand": "Parle-G",
        "product_name": "Parle-G Biscuits 800g",
        "batch_number": "P12F9",
    },
]


def seed():
    db = SessionLocal()
    try:
        added = 0
        for item in DEMO_PRODUCTS:
            exists = (
                db.query(models.Product)
                .filter(models.Product.qr_code_id == item["qr_code_id"])
                .first()
            )
            if not exists:
                db.add(models.Product(**item))
                added += 1
        db.commit()
        print(f"Seeded {added} new demo product(s). {len(DEMO_PRODUCTS)} total in seed list.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
