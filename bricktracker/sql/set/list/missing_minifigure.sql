{% extends 'set/base/full.sql' %}

{% block where %}
WHERE "bricktracker_sets"."id" IN (
    SELECT
        "missing"."u_id"
    FROM "missing"

    WHERE "missing"."set_num" IS NOT DISTINCT FROM :figure

    GROUP BY "missing"."u_id"
)
{% endblock %}
