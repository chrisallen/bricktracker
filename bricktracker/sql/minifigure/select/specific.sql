{% extends 'minifigure/base/select.sql' %}

{% block where %}
WHERE fig_num IS NOT DISTINCT FROM :fig_num
AND u_id IS NOT DISTINCT FROM :u_id
AND set_num IS NOT DISTINCT FROM :set_num
{% endblock %}
