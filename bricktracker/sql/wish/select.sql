{% extends 'wish/base/select.sql' %}

{% block where %}
WHERE "wishlist"."set_num" IS NOT DISTINCT FROM :set_num
{% endblock %}
