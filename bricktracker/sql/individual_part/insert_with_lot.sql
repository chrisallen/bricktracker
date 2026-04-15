-- Insert an individual part that belongs to a lot
INSERT INTO "bricktracker_individual_parts" (
    "id",
    "part",
    "color",
    "quantity",
    "missing",
    "damaged",
    "checked",
    "description",
    "storage",
    "purchase_location",
    "purchase_date",
    "purchase_price",
    "lot_id"
) VALUES (
    :id,
    :part,
    :color,
    :quantity,
    0,
    0,
    0,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    :lot_id
)
