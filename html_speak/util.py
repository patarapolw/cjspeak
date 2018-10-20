import regex

RE_IS_HTML = regex.compile(r"(?:</[^<]+>)|(?:<[^<]+/>)")


def is_html(s):
    return RE_IS_HTML.search(s) is not None
