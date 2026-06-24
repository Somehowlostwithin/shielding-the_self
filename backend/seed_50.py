"""
Generates 50 demo products for testing/verification, with unique QR codes
across a spread of common Indian FMCG brands.

Run from inside backend/:
    python seed_50.py

This ADDS to whatever's already in your database — it won't duplicate
products if you run it twice (checks by qr_code_id first).
"""

from database import Base, SessionLocal, engine
import models

Base.metadata.create_all(bind=engine)

# (brand, product_name template, batch prefix, how many variants to generate)
BRAND_CATALOG = [
    ("Sensodyne", "Sensodyne Rapid Relief Toothpaste", "B23"),
    ("Amul", "Amul Gold Milk 1L", "A45"),
    ("Colgate", "Colgate Total Toothpaste", "C19"),
    ("Dettol", "Dettol Antiseptic Liquid", "D88"),
    ("Parle-G", "Parle-G Biscuits 800g", "P12"),
    ("Surf Excel", "Surf Excel Easy Wash 1kg", "S77"),
    ("Maggi", "Maggi 2-Minute Noodles 70g", "M34"),
    ("Lifebuoy", "Lifebuoy Total Soap 125g", "L56"),
    ("Tata Salt", "Tata Salt Iodised 1kg", "T09"),
    ("Britannia", "Britannia Good Day Biscuits", "BR21"),
]

PRODUCTS_PER_BRAND = 5  # 10 brands x 5 = 50 unique QR codes

# one deliberately reused "fake" code per brand for guaranteed-FAKE demo scans
FAKE_SUFFIX = "FAKE"


def generate_products():
    products = []
    for brand, product_name, batch_prefix in BRAND_CATALOG:
        brand_code = "".join(ch for ch in brand.upper() if ch.isalnum())[:4]
        for i in range(1, PRODUCTS_PER_BRAND + 1):
            qr_code_id = f"{brand_code}-{i:04d}"
            batch_number = f"{batch_prefix}{i}"
            products.append({
                "qr_code_id": qr_code_id,
                "brand": brand,
                "product_name": product_name,
                "batch_number": batch_number,
            })
    return products


def seed():
    db = SessionLocal()
    try:
        products = generate_products()
        added = 0
        for item in products:
            exists = (
                db.query(models.Product)
                .filter(models.Product.qr_code_id == item["qr_code_id"])
                .first()
            )
            if not exists:
                db.add(models.Product(**item))
                added += 1
        db.commit()
        print(f"Seeded {added} new product(s). {len(products)} total in this batch.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
