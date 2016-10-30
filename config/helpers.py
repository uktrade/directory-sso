import tldextract
from urllib.parse import urlparse


def validate_domain(domain):
    # NOTE: tldextract and urlparse both have their shortcomings so
    # using both for what they do good
    tld_result = tldextract.extract(domain)
    if tld_result.domain and tld_result.suffix and not tld_result.subdomain:
        urlparse_result = urlparse(domain)
        if not urlparse_result.scheme:
            # When no scheme given urlparse doesn't correctly identify
            # all parts of the url, so adding it temporarily
            urlparse_result = urlparse('http://' + domain)
        if urlparse_result.path or urlparse_result.query:
            return False
        return True
    return False
