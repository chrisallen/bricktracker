INSERT OR IGNORE INTO "bricktracker_sets" (
    "id",
    "set",
    "storage",
    "purchase_location",
    "purchase_date",
    "purchase_price",
    "description"
) VALUES (
    :id,
    :set,
    :storage,
    :purchase_location,
    :purchase_date,
    :purchase_price,
    :description
)
