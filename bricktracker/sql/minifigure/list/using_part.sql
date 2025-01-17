{% extends 'minifigure/base/select.sql' %}

{% block where %}
WHERE minifigures.fig_num IN (
    SELECT
        inventory.set_num
    FROM inventory

    WHERE inventory.color_id IS NOT DISTINCT FROM :color_id
    AND inventory.element_id IS NOT DISTINCT FROM :element_id
    AND inventory.part_num IS NOT DISTINCT FROM :part_num

    GROUP BY inventory.set_num
)
{% endblock %}
