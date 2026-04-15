-- List all individual minifigures
SELECT
    "bricktracker_individual_minifigures"."id",
    "bricktracker_individual_minifigures"."figure",
    "bricktracker_individual_minifigures"."quantity",
    "bricktracker_individual_minifigures"."description",
    "bricktracker_individual_minifigures"."storage",
    "bricktracker_individual_minifigures"."purchase_location",
    "rebrickable_minifigures"."number",
    "rebrickable_minifigures"."name",
    "rebrickable_minifigures"."image",
    "rebrickable_minifigures"."number_of_parts",
    0 AS "total_missing",
    0 AS "total_damaged"{% if owners %},
    {{ owners }}{% endif %}{% if statuses %},
    {{ statuses }}{% endif %}{% if tags %},
    {{ tags }}{% endif %}
FROM "bricktracker_individual_minifigures"

INNER JOIN "rebrickable_minifigures"
    ON "bricktracker_individual_minifigures"."figure" = "rebrickable_minifigures"."figure"

-- LEFT JOINs for metadata (owners, statuses, tags use separate dynamic column tables)
LEFT JOIN "bricktracker_set_owners"
    ON "bricktracker_individual_minifigures"."id" = "bricktracker_set_owners"."id"

LEFT JOIN "bricktracker_set_statuses"
    ON "bricktracker_individual_minifigures"."id" = "bricktracker_set_statuses"."id"

LEFT JOIN "bricktracker_set_tags"
    ON "bricktracker_individual_minifigures"."id" = "bricktracker_set_tags"."id"

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}

{% if offset %}
OFFSET {{ offset }}
{% endif %}
