INSERT OR IGNORE INTO "rebrickable_minifigures" (
    "figure",
    "number",
    "name",
    "image"
) VALUES (
    :figure,
    :number,
    :name,
    :image
)
ON CONFLICT("figure")
DO UPDATE SET
"number" = :number,
"name" = :name,
"image" = :image
WHERE "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM :figure
