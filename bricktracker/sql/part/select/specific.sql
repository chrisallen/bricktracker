{% extends 'part/base/select.sql' %}

{% block join %}
LEFT JOIN missing
ON inventory.set_num IS NOT DISTINCT FROM missing.set_num
AND inventory.id IS NOT DISTINCT FROM missing.id
AND inventory.u_id IS NOT DISTINCT FROM missing.u_id
{% endblock %}

{% block where %}
WHERE inventory.u_id IS NOT DISTINCT FROM :u_id
AND inventory.set_num IS NOT DISTINCT FROM :set_num
AND inventory.id IS NOT DISTINCT FROM :id
{% endblock %}

{% block group %}
GROUP BY
    inventory.set_num,
    inventory.id,
    inventory.part_num,
    inventory.color_id,
    inventory.element_id,
    inventory.u_id
{% endblock %}
