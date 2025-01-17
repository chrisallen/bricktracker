{% extends 'part/base/select.sql' %}

{% block total_missing %}
SUM(IFNULL(missing.quantity, 0)) AS total_missing,
{% endblock %}

{% block total_quantity %}
SUM(IFNULL((NOT inventory.is_spare) * inventory.quantity, 0)) AS total_quantity,
{% endblock %}

{% block total_spare %}
SUM(IFNULL(inventory.is_spare * inventory.quantity, 0)) AS total_spare,
{% endblock %}

{% block join %}
LEFT JOIN missing
ON inventory.set_num IS NOT DISTINCT FROM missing.set_num
AND inventory.id IS NOT DISTINCT FROM missing.id
AND inventory.part_num IS NOT DISTINCT FROM missing.part_num
AND inventory.color_id IS NOT DISTINCT FROM missing.color_id
AND inventory.element_id IS NOT DISTINCT FROM missing.element_id
AND inventory.u_id IS NOT DISTINCT FROM missing.u_id
{% endblock %}

{% block where %}
WHERE inventory.part_num IS NOT DISTINCT FROM :part_num
AND inventory.color_id IS NOT DISTINCT FROM :color_id
AND inventory.element_id IS NOT DISTINCT FROM :element_id
{% endblock %}

{% block group %}
GROUP BY
    inventory.part_num,
    inventory.color_id,
    inventory.element_id
{% endblock %}
