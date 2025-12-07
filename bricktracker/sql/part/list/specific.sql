
{% extends 'part/base/base.sql' %}

{% block total_missing %}
IFNULL("bricktracker_parts"."missing", 0) AS "total_missing",
{% endblock %}

{% block total_damaged %}
IFNULL("bricktracker_parts"."damaged", 0) AS "total_damaged",
{% endblock %}

{% block where %}
{% set conditions = [] %}
{% set _ = conditions.append('"bricktracker_parts"."id" IS NOT DISTINCT FROM :id') %}
{% set _ = conditions.append('"bricktracker_parts"."figure" IS NOT DISTINCT FROM :figure') %}
{% if skip_spare_parts %}
  {% set _ = conditions.append('"bricktracker_parts"."spare" = 0') %}
{% endif %}
WHERE {{ conditions | join(' AND ') }}
{% endblock %}
