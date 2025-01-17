{% extends 'minifigure/base/select.sql' %}

{% block total_missing %}
SUM(IFNULL(missing.quantity, 0)) AS total_missing,
{% endblock %}

{% block join %}
LEFT JOIN missing
ON minifigures.fig_num IS NOT DISTINCT FROM missing.set_num
AND minifigures.u_id IS NOT DISTINCT FROM missing.u_id
{% endblock %}

{% block group %}
GROUP BY
    minifigures.fig_num,
    minifigures.u_id
{% endblock %}
