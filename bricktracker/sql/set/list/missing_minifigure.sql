{% extends 'set/base/full.sql' %}

{% block where %}
WHERE "bricktracker_sets"."id" IN (
    SELECT
        "missing"."u_id"
    FROM "missing"

    WHERE "missing"."set_num" IS NOT DISTINCT FROM :fig_num

    GROUP BY "missing"."u_id"
)
{% endblock %}
