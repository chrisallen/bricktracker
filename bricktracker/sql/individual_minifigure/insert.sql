INSERT OR IGNORE INTO "bricktracker_individual_minifigures" (
    "id",
    "figure",
    "quantity",
    "description",
    "storage",
    "purchase_location",
    "purchase_date",
    "purchase_price"
) VALUES (
    :id,
    :figure,
    :quantity,
    :description,
    :storage,
    :purchase_location,
    :purchase_date,
    :purchase_price
)
