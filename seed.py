from app import app, db, PackagingStandard

with app.app_context():

    PackagingStandard.query.delete()

    db.session.add_all([
        PackagingStandard(
            category="cosmetics",
            primary_packaging="PP Twist Tube",
            secondary_packaging="Printed Paperboard Carton",
            fragility_level="M"
        ),
        PackagingStandard(
            category="food",
            primary_packaging="Molded Pulp Tray",
            secondary_packaging="Corrugated Carton",
            fragility_level="L"
        ),
        PackagingStandard(
            category="electronics",
            primary_packaging="Foam Cushioning",
            secondary_packaging="Double Wall Corrugated Box",
            fragility_level="H"
        ),
        PackagingStandard(
            category="pharma",
            primary_packaging="Blister Pack",
            secondary_packaging="Carton Box",
            fragility_level="M"
        ),
        PackagingStandard(
            category="fragile",
            primary_packaging="Bubble Wrap",
            secondary_packaging="Heavy Corrugated Box",
            fragility_level="H"
        )
    ])

    db.session.commit()
    print("Packaging standards seeded!")
