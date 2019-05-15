import tldextract
from urllib.parse import urlparse
import hashlib


def createHash(id):
    """This function generate 64 character long hash"""

    hash = hashlib.sha256(str(id).encode('utf-8'))
    return hash.hexdigest()


def is_valid_domain(domain):
    # NOTE: tldextract and urlparse both have their shortcomings so
    # using both for what they do good
    # add local domain suffix because it is non-standard
    extract_with_extra_suffix = tldextract.TLDExtract(
        extra_suffixes=["great"],
    )
    tld_result = extract_with_extra_suffix(domain)
    urlparse_result = urlparse(domain)

    is_domain = tld_result.domain and tld_result.suffix
    has_subdomain = bool(tld_result.subdomain)
    is_suffix = (tld_result.suffix and not tld_result.domain
                 and not tld_result.subdomain)
    has_scheme = bool(urlparse_result.scheme)

    if is_domain and not has_subdomain:
        if not has_scheme:
            # When no scheme given urlparse doesn't correctly identify
            # all parts of the url, so adding it temporarily
            urlparse_result = urlparse('http://' + domain)
        if urlparse_result.path or urlparse_result.query:
            return False
        return True
    elif is_suffix and not has_scheme:
        # http://.com or http://com just looks weird and
        # is likely a mistake, hence only accepting .com and com
        return True
    return False
