{% extends 'set/base/full.sql' %}

{% block where %}
WHERE "bricktracker_sets"."id" IN (
    SELECT
        "inventory"."u_id"
    FROM "inventory"

    WHERE "inventory"."set_num" IS NOT DISTINCT FROM :figure

    GROUP BY "inventory"."u_id"
)
{% endblock %}
