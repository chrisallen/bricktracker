{% extends 'part/base/base.sql' %}

{% block total_missing %}
"combined"."missing" AS "total_missing",
{% endblock %}

{% block total_damaged %}
"combined"."damaged" AS "total_damaged",
{% endblock %}

{% block total_quantity %}
"combined"."quantity" AS "total_quantity",
{% endblock %}

{% block total_spare %}
"combined"."spare" AS "total_spare",
{% endblock %}

{% block total_sets %}
1 AS "total_sets",
{% endblock %}

{% block total_minifigures %}
CASE WHEN "combined"."figure" IS NOT NULL THEN 1 ELSE 0 END AS "total_minifigures"
{% endblock %}

{% block where %}
{% set conditions = [] %}
{% if skip_spare_parts %}
  {% set _ = conditions.append('"combined"."spare" = 0') %}
{% endif %}
{% if conditions %}
WHERE {{ conditions | join(' AND ') }}
{% endif %}
{% endblock %}
