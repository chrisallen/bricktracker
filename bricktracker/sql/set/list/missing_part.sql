{% extends 'set/base/select.sql' %}

{% block where %}
WHERE sets.u_id IN (
    SELECT
        missing.u_id
    FROM missing

    WHERE missing.color_id IS NOT DISTINCT FROM :color_id
    AND missing.element_id IS NOT DISTINCT FROM :element_id
    AND missing.part_num IS NOT DISTINCT FROM :part_num

    GROUP BY missing.u_id
)
{% endblock %}
