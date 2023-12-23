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

import logging
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    raise ImportError('requests library missing. pip install requests')


def Get(url, headers={}, timeout=5, allow_redirects=True, cookies=None, params=None):
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=timeout, allow_redirects=allow_redirects,
                            cookies=cookies)
    except Exception as e:
        logging.error(e)
        return None, e
    return resp, None


def Post(url, data={}, headers={}, timeout=15, cookies=None):
    try:
        resp = requests.post(url, data=data, headers=headers, cookies=cookies, timeout=timeout)
    except Exception as e:
        logging.error(e)
        return None, e
    return resp, None


def send_raw_request(host, raw_request):
    raw_request = raw_request.replace("\\r", "\r").replace("\\n", "\n")
    try:
        method = raw_request.split("\r\n")[0].split(" ")[0]
        path = raw_request.split("\r\n")[0].split(" ")[1]
        headers_string = raw_request.split("\r\n\r\n")[0].split("\r\n")[1:]
        headers = {}
        cookies = {}
        for string in headers_string:
            if string.split(":", 1)[0].strip() == 'Cookie':
                for cookies_info in string.split(":", 1)[0].strip().split(';'):
                    cookies[cookies_info.split(':', 1)[0]] = cookies_info.split(':', 1)[1]
                continue
            headers[string.split(":", 1)[0].strip()] = string.split(":", 1)[1].strip()
        body = None
        if len(raw_request.split("\r\n\r\n", 1)) != 1:
            body = raw_request.split("\r\n\r\n", 1)[1]
        host = urljoin(headers["Host"] or host, path)
        resp = getattr(requests, method.lower())(host, headers=headers, data=body, cookies=cookies)
    except Exception as e:
        logging.error(e)
        return None, e
    return resp, None
