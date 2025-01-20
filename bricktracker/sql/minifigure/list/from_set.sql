{% extends 'minifigure/base/select.sql' %}

{% block where %}
WHERE "minifigures"."u_id" IS NOT DISTINCT FROM :u_id
AND "minifigures"."set_num" IS NOT DISTINCT FROM :set_num
{% endblock %}
