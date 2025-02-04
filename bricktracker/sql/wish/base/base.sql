SELECT
    "bricktracker_wishes"."set",
    "bricktracker_wishes"."name",
    "bricktracker_wishes"."year",
    "bricktracker_wishes"."theme_id",
    "bricktracker_wishes"."number_of_parts",
    "bricktracker_wishes"."image",
    {% block owners %}
        {% if owners %}{{ owners }},{% endif %}
    {% endblock %}
    "bricktracker_wishes"."url"
FROM "bricktracker_wishes"

{% if owners %}
LEFT JOIN "bricktracker_wish_owners"
ON "bricktracker_wishes"."set" IS NOT DISTINCT FROM "bricktracker_wish_owners"."set"
{% endif %}

{% block where %}{% endblock %}

{% if order %}
ORDER BY {{ order }}
{% endif %}

{% if limit %}
LIMIT {{ limit }}
{% endif %}
