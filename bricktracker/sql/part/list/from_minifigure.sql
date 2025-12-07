
{% extends 'part/base/base.sql' %}

{% block total_missing %}
SUM("bricktracker_parts"."missing") AS "total_missing",
{% endblock %}

{% block total_damaged %}
SUM("bricktracker_parts"."damaged") AS "total_damaged",
{% endblock %}

{% block where %}
{% set conditions = [] %}
{% set _ = conditions.append('"bricktracker_parts"."figure" IS NOT DISTINCT FROM :figure') %}
{% if skip_spare_parts %}
  {% set _ = conditions.append('"bricktracker_parts"."spare" = 0') %}
{% endif %}
WHERE {{ conditions | join(' AND ') }}
{% endblock %}

{% block group %}
GROUP BY
    "bricktracker_parts"."part",
    "bricktracker_parts"."color",
    "bricktracker_parts"."spare"
{% endblock %}
