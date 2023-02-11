from urllib.parse import urlparse, urljoin
from flask import request


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def to_input_format(text):
    new_text = ''
    for line in text.splitlines():
        if line.strip() == '':
            continue
        new_text += line.strip() + '\n'
    return new_text
