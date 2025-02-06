INSERT OR IGNORE INTO "rebrickable_minifigures" (
    "figure",
    "number",
    "name",
    "image",
    "number_of_parts"
) VALUES (
    :figure,
    :number,
    :name,
    :image,
    :number_of_parts
)
ON CONFLICT("figure")
DO UPDATE SET
"number" = :number,
"name" = :name,
"image" = :image,
"number_of_parts" = :number_of_parts
WHERE "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM :figure
