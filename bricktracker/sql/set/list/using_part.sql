{% extends 'set/base/full.sql' %}

{% block where %}
WHERE "bricktracker_sets"."id" IN (
    SELECT "bricktracker_parts"."id"
    FROM "bricktracker_parts"
    WHERE "bricktracker_parts"."part" IS NOT DISTINCT FROM :part
    AND "bricktracker_parts"."color" IS NOT DISTINCT FROM :color
    GROUP BY "bricktracker_parts"."id"
)
{% endblock %}
