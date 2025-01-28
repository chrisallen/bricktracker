{% extends 'set/base/full.sql' %}

{% block where %}
WHERE "bricktracker_sets"."id" IN (
    SELECT "bricktracker_parts"."id"
    FROM "bricktracker_parts"
    WHERE "bricktracker_parts"."figure" IS NOT DISTINCT FROM :figure
    GROUP BY "bricktracker_parts"."id"
)
{% endblock %}
