{% extends 'set/base/select.sql' %}

{% block where %}
WHERE "sets"."u_id" IN (
    SELECT
        "inventory"."u_id"
    FROM "inventory"

    WHERE "inventory"."set_num" IS NOT DISTINCT FROM :fig_num

    GROUP BY "inventory"."u_id"
)
{% endblock %}
