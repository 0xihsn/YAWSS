"""

     Copyright (C) 2020  IHSAN BILKAY

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>

"""

import hashlib
from urllib.parse import urlparse, urlunparse, urljoin, parse_qsl, urlencode


def url_check(url, base_url):
    if url:
        url = url.replace("*", "")
        base_url_parts = urlparse(base_url)
    else:
        return None
    try:
        parsed_url = urlparse(url)
    except UnicodeError as e:
        return None
    if parsed_url.scheme == 'http' or parsed_url.scheme == 'https' or parsed_url.scheme == '':
        if parsed_url.netloc != base_url_parts.netloc and parsed_url.netloc != '':
            return None
        return urljoin(base_url, url)
    return None


def url_unparse(urlparts, scheme=None, netloc=None, path=None, params=None, query=None, fragment=None):
    return urlunparse(((scheme or urlparts.scheme),
                       (netloc or urlparts.netloc),
                       (path or urlparts.path),
                       (params or urlparts.params),
                       (query or urlparts.query),
                       (fragment or urlparts.fragment)))


def queries_check(url, base_url, queries_hashes):
    if url:
        url = url.replace("*", "")
        base_url_parts = urlparse(base_url)
    else:
        return None
    try:
        parsed_url = urlparse(url)
    except UnicodeError as e:
        return None
    if parsed_url.scheme == 'http' or parsed_url.scheme == 'https' or parsed_url.scheme == '':
        if parsed_url.netloc != base_url_parts.netloc and parsed_url.netloc != '':
            return None
        url_parts = list(parsed_url)
        query = dict(parse_qsl(parsed_url.query))
        mod_query = {k: 'YAWSS' for k in query}
        url_parts[4] = urlencode(mod_query)
        mod_url = urlunparse(url_parts)
        q_hash = hashlib.sha1(mod_url.encode()).hexdigest()
        if q_hash in queries_hashes:
            return False
        else:
            queries_hashes.add(q_hash)
            return True
    return None
