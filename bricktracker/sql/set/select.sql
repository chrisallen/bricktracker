{% extends 'set/base/select.sql' %}

{% block where_missing %}
WHERE "missing"."u_id" IS NOT DISTINCT FROM :u_id
{% endblock %}

{% block where_minifigures %}
WHERE "minifigures"."u_id" IS NOT DISTINCT FROM :u_id
{% endblock %}

{% block where %}
WHERE "sets"."u_id" IS NOT DISTINCT FROM :u_id
{% endblock %}
