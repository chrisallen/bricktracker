"""Custom Jinja2 template filters for BrickTracker."""

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def replace_query_filter(url, key, value):
    """Replace or add a query parameter in a URL"""
    parsed = urlparse(url)
    query_dict = parse_qs(parsed.query, keep_blank_values=True)
    query_dict[key] = [str(value)]

    new_query = urlencode(query_dict, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))