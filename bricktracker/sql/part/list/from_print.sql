
{% extends 'part/base/base.sql' %}

{% block total_missing %}{% endblock %}

{% block total_damaged %}{% endblock %}

{# Per part+color set/minifigure counts so each sub-card shows its own totals
   (same #159 inherited-count bug as with_different_color). Mirrors all.sql. #}
{% block total_sets %}
IFNULL(COUNT(DISTINCT CASE WHEN "combined"."source_type" = 'set' THEN "combined"."id" ELSE NULL END), 0) AS "total_sets",
{% endblock %}

{% block total_minifigures %}
SUM(IFNULL("minifigure_quantities"."quantity", 0)) AS "total_minifigures"
{% endblock %}

{% block join %}
-- Join to get minifigure quantities from both set-based and individual minifigures
LEFT JOIN (
    SELECT
        "bricktracker_minifigures"."id",
        "bricktracker_minifigures"."figure",
        "bricktracker_minifigures"."quantity"
    FROM "bricktracker_minifigures"

    UNION ALL

    SELECT
        "bricktracker_individual_minifigures"."id",
        "bricktracker_individual_minifigures"."figure",
        "bricktracker_individual_minifigures"."quantity"
    FROM "bricktracker_individual_minifigures"
) AS "minifigure_quantities"
ON "combined"."id" IS NOT DISTINCT FROM "minifigure_quantities"."id"
AND "combined"."figure" IS NOT DISTINCT FROM "minifigure_quantities"."figure"
{% endblock %}

{% block where %}
WHERE "rebrickable_parts"."print" IS NOT DISTINCT FROM :print
AND "combined"."color" IS NOT DISTINCT FROM :color
AND "combined"."part" IS DISTINCT FROM :part
{% endblock %}

{% block group %}
GROUP BY
    "combined"."part",
    "combined"."color"
{% endblock %}
