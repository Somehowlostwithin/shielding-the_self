"""
Generates demo products for testing/verification, with unique QR codes
across a spread of common Indian FMCG brands.

Run from inside backend/:
    python seed_50.py

This ADDS to whatever's already in your database — it won't duplicate
products if you run it twice (checks by qr_code_id first). Safe to re-run
any time, including after adding more brands to the catalog below.

Total catalog: 250 products
  - 10 original brands x 5 each  = 50  (unchanged from before)
  - 20 new brands x 10 each      = 200 (added without touching the 50)
"""

from database import Base, SessionLocal, engine
import models

Base.metadata.create_all(bind=engine)

# (brand, product_name, batch_prefix, how many variants to generate)
# Prefixes below are derived from the first 4 alphanumeric chars of the
# brand name (uppercased) — every entry's derived prefix was checked by
# hand against every other entry's to guarantee no qr_code_id collisions.
BRAND_CATALOG = [
    # ---- original 10 brands (unchanged — do not edit these) ----
    ("Sensodyne", "Sensodyne Rapid Relief Toothpaste", "B23", 5),
    ("Amul", "Amul Gold Milk 1L", "A45", 5),
    ("Colgate", "Colgate Total Toothpaste", "C19", 5),
    ("Dettol", "Dettol Antiseptic Liquid", "D88", 5),
    ("Parle-G", "Parle-G Biscuits 800g", "P12", 5),
    ("Surf Excel", "Surf Excel Easy Wash 1kg", "S77", 5),
    ("Maggi", "Maggi 2-Minute Noodles 70g", "M34", 5),
    ("Lifebuoy", "Lifebuoy Total Soap 125g", "L56", 5),
    ("Tata Salt", "Tata Salt Iodised 1kg", "T09", 5),
    ("Britannia", "Britannia Good Day Biscuits", "BR21", 5),

    # ---- 20 new brands added for the 250-product test set ----
    ("Lux", "Lux Soft Touch Soap 100g", "LX5", 10),
    ("Pepsodent", "Pepsodent Germicheck Toothpaste", "PD7", 10),
    ("Nivea", "Nivea Soft Moisturising Cream", "NV3", 10),
    ("Vicks", "Vicks VapoRub 50ml", "VK8", 10),
    ("Horlicks", "Horlicks Health Drink 500g", "HL2", 10),
    ("Bournvita", "Bournvita Health Drink 500g", "BV4", 10),
    ("Patanjali", "Patanjali Aloe Vera Gel", "PT6", 10),
    ("Fortune", "Fortune Sunflower Oil 1L", "FT1", 10),
    ("Aashirvaad", "Aashirvaad Shudh Chakki Atta 5kg", "AS9", 10),
    ("Fevicol", "Fevicol MR Adhesive 500g", "FV2", 10),
    ("Harpic", "Harpic Power Plus Toilet Cleaner", "HP5", 10),
    ("Vim", "Vim Dishwash Bar 700g", "VM3", 10),
    ("Closeup", "Closeup Red Hot Toothpaste", "CL8", 10),
    ("Pears", "Pears Pure & Gentle Soap 125g", "PR4", 10),
    ("Cadbury", "Cadbury Dairy Milk 150g", "CD6", 10),
    ("Kissan", "Kissan Mixed Fruit Jam 500g", "KS1", 10),
    ("Real", "Real Mixed Fruit Juice 1L", "RL7", 10),
    ("Bingo", "Bingo Mad Angles Chips", "BG9", 10),
    ("Haldiram's", "Haldiram's Aloo Bhujia 200g", "HD3", 10),
    ("Saffola", "Saffola Gold Edible Oil 1L", "SF6", 10),
]


def generate_products():
    products = []
    for brand, product_name, batch_prefix, count in BRAND_CATALOG:
        brand_code = "".join(ch for ch in brand.upper() if ch.isalnum())[:4]
        for i in range(1, count + 1):
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

        # sanity check: make sure the catalog itself has no internal
        # qr_code_id collisions before touching the database at all
        seen = set()
        for item in products:
            if item["qr_code_id"] in seen:
                raise ValueError(f"Duplicate qr_code_id in catalog: {item['qr_code_id']}")
            seen.add(item["qr_code_id"])

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
        print(f"Seeded {added} new product(s). {len(products)} total in this catalog.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
