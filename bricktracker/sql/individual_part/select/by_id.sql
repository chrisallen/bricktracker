-- Select a specific individual part by UUID
SELECT
    "bricktracker_individual_parts"."id",
    "bricktracker_individual_parts"."part",
    "bricktracker_individual_parts"."color",
    "bricktracker_individual_parts"."quantity",
    "bricktracker_individual_parts"."missing",
    "bricktracker_individual_parts"."damaged",
    "bricktracker_individual_parts"."checked",
    "bricktracker_individual_parts"."description",
    "bricktracker_individual_parts"."lot_id",
    "bricktracker_individual_parts"."storage",
    "bricktracker_individual_parts"."purchase_location",
    "bricktracker_individual_parts"."purchase_date",
    "bricktracker_individual_parts"."purchase_price",
    "rebrickable_parts"."name" AS "part_name",
    "rebrickable_parts"."color_name",
    "rebrickable_parts"."color_rgb",
    "rebrickable_parts"."color_transparent",
    "rebrickable_parts"."category",
    "rebrickable_parts"."image",
    "rebrickable_parts"."image_id",
    "rebrickable_parts"."url",
    "rebrickable_parts"."bricklink_part_num",
    "rebrickable_parts"."bricklink_color_id",
    "rebrickable_parts"."bricklink_color_name"
    {% if owners %},{{ owners }}{% endif %}
    {% if statuses %},{{ statuses }}{% endif %}
    {% if tags %},{{ tags }}{% endif %}
FROM "bricktracker_individual_parts"
INNER JOIN "rebrickable_parts"
    ON "bricktracker_individual_parts"."part" = "rebrickable_parts"."part"
    AND "bricktracker_individual_parts"."color" = "rebrickable_parts"."color_id"

LEFT JOIN "bricktracker_set_owners"
ON "bricktracker_individual_parts"."id" IS NOT DISTINCT FROM "bricktracker_set_owners"."id"

LEFT JOIN "bricktracker_set_statuses"
ON "bricktracker_individual_parts"."id" IS NOT DISTINCT FROM "bricktracker_set_statuses"."id"

LEFT JOIN "bricktracker_set_tags"
ON "bricktracker_individual_parts"."id" IS NOT DISTINCT FROM "bricktracker_set_tags"."id"

WHERE "bricktracker_individual_parts"."id" = :id;
