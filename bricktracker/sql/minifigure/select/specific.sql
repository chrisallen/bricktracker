{% extends 'minifigure/base/select.sql' %}

{% block where %}
WHERE "minifigures"."fig_num" IS NOT DISTINCT FROM :fig_num
AND "minifigures"."u_id" IS NOT DISTINCT FROM :u_id
AND "minifigures"."set_num" IS NOT DISTINCT FROM :set_num
{% endblock %}
