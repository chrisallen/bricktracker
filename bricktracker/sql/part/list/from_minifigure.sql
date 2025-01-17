
{% extends 'part/base/select.sql' %}

{% block total_missing %}
SUM(IFNULL(missing.quantity, 0)) AS total_missing,
{% endblock %}

{% block join %}
LEFT JOIN missing
ON missing.set_num IS NOT DISTINCT FROM inventory.set_num
AND missing.id IS NOT DISTINCT FROM inventory.id
AND missing.part_num IS NOT DISTINCT FROM inventory.part_num
AND missing.color_id IS NOT DISTINCT FROM inventory.color_id
AND missing.element_id IS NOT DISTINCT FROM inventory.element_id
{% endblock %}

{% block where %}
WHERE inventory.set_num IS NOT DISTINCT FROM :set_num
{% endblock %}

{% block group %}
GROUP BY
    inventory.part_num,
    inventory.name,
    inventory.color_id,
    inventory.is_spare,
    inventory.element_id
{% endblock %}
