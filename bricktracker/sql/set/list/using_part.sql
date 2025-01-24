{% extends 'set/base/full.sql' %}

{% block where %}
WHERE "bricktracker_sets"."id" IN (
    SELECT
        "inventory"."u_id"
    FROM "inventory"

    WHERE "inventory"."color_id" IS NOT DISTINCT FROM :color_id
    AND "inventory"."element_id" IS NOT DISTINCT FROM :element_id
    AND "inventory"."part_num" IS NOT DISTINCT FROM :part_num

    GROUP BY "inventory"."u_id"
)
{% endblock %}
