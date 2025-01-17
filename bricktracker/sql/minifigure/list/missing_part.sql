{% extends 'minifigure/base/select.sql' %}

{% block where %}
WHERE minifigures.fig_num IN (
    SELECT
        missing.set_num
    FROM missing

    WHERE missing.color_id IS NOT DISTINCT FROM :color_id
    AND missing.element_id IS NOT DISTINCT FROM :element_id
    AND missing.part_num IS NOT DISTINCT FROM :part_num

    GROUP BY missing.set_num
)
{% endblock %}
