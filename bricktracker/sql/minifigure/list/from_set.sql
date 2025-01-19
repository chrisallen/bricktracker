{% extends 'minifigure/base/select.sql' %}

{% block where %}
WHERE u_id IS NOT DISTINCT FROM :u_id
AND set_num IS NOT DISTINCT FROM :set_num
{% endblock %}
