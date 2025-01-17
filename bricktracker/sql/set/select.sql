{% extends 'set/base/select.sql' %}

{% block where_missing %}
WHERE u_id IS NOT DISTINCT FROM :u_id
{% endblock %}

{% block where_minifigures %}
WHERE u_id IS NOT DISTINCT FROM :u_id
{% endblock %}

{% block where %}
WHERE sets.u_id IS NOT DISTINCT FROM :u_id
{% endblock %}
