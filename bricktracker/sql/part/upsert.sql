INSERT INTO "bricktracker_parts" (
    "id",
    "figure",
    "part",
    "color",
    "spare",
    "quantity",
    "element",
    "rebrickable_inventory",
    "checked",
    "missing",
    "damaged"
) VALUES (
    :id,
    :figure,
    :part,
    :color,
    :spare,
    :quantity,
    :element,
    :rebrickable_inventory,
    0,
    0,
    0
)
ON CONFLICT("id", "figure", "part", "color", "spare")
DO UPDATE SET
    "quantity" = excluded."quantity",
    "element" = excluded."element",
    "rebrickable_inventory" = excluded."rebrickable_inventory"
