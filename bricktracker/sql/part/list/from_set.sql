
{% extends 'part/base/select.sql' %}

{% block total_missing %}
IFNULL(missing.quantity, 0) AS total_missing,
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
WHERE inventory.u_id IS NOT DISTINCT FROM :u_id
AND inventory.set_num IS NOT DISTINCT FROM :set_num
{% endblock %}
