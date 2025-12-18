{% extends 'set/base/full.sql' %}

{% block where %}
{% if search_query %}
WHERE (LOWER("rebrickable_sets"."name") LIKE LOWER('%{{ search_query }}%')
   OR LOWER("rebrickable_sets"."set") LIKE LOWER('%{{ search_query }}%'))
{% endif %}
{% endblock %}
