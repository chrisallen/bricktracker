{% extends 'minifigure/base/base.sql' %}

{% block total_missing %}
SUM("bricktracker_parts"."missing") AS "total_missing",
{% endblock %}

{% block total_damaged %}
SUM("bricktracker_parts"."damaged") AS "total_damaged",
{% endblock %}

{% block join %}
LEFT JOIN "bricktracker_parts"
ON "bricktracker_minifigures"."id" IS NOT DISTINCT FROM "bricktracker_parts"."id"
AND "rebrickable_minifigures"."figure" IS NOT DISTINCT FROM "bricktracker_parts"."figure"
{% endblock %}

{% block where %}
-- rebrickable_minifigures is a catalog cache that keeps entries after a set is
-- deleted, so only keep figures still owned through a set or individually
WHERE "bricktracker_minifigures"."figure" IS NOT NULL
OR EXISTS (
    SELECT 1
    FROM "bricktracker_individual_minifigures"
    WHERE "bricktracker_individual_minifigures"."figure" IS NOT DISTINCT FROM "rebrickable_minifigures"."figure"
)
{% endblock %}

{% block group %}
GROUP BY
    "rebrickable_minifigures"."figure",
    "bricktracker_minifigures"."id"
{% endblock %}
