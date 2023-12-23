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

import ipaddress
import logging
from urllib.parse import urlparse

from core.utils.colorize import c
from core.utils.network import Get

try:
    import psycopg2
    import OpenSSL
    import ssl
except ImportError as e:
    logging.error('Library missing. pip install -r requirements')
    raise ImportError('Library missing. pip install -r requirements')


def connect_to_db():
    DB_HOST = 'crt.sh'
    DB_NAME = 'certwatch'
    DB_USER = 'guest'
    DB_PASSWORD = ''
    cursor = None
    try:
        conn = psycopg2.connect('dbname={0} user={1} host={2}'.format(DB_NAME, DB_USER, DB_HOST))
        conn.autocommit = True
        cursor = conn.cursor()
    except Exception as e:
        logging.error('failed to connect to crt.sh database')
    return cursor


def get_cert(target, port=443):
    conn = ssl.create_connection((target, port))
    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sock = context.wrap_socket(conn, server_hostname=target)
    return ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))


def get_subdomains(target):
    try:
        ipaddress.ip_address(target)
    except ValueError as e:
        print(c('[!] subdomain scan is not supported for this target.', 'Red'))
        logging.info('subdomain scan is not supported for this target')
        return set()
    try:
        target = urlparse(target).hostname.split('.', 1)[1]
    except Exception as e:
        print(c('[x] subdomain scan is not supported for this target.', 'Red'))
        logging.info('subdomain scan is not supported for this target, {e}')
        return set()

    subdomains_list = set()
    cursor = connect_to_db()
    if cursor:
        try:
            cursor.execute(
                'SELECT ci.NAME_VALUE NAME_VALUE \
                 FROM certificate_identity ci \
                 WHERE ci.NAME_TYPE = \'dNSName\' AND reverse(lower(ci.NAME_VALUE)) LIKE reverse(lower(\'%.{}\'));'
                    .format(target))
        except Exception as e:
            logging.error('failed to get the subdomain list from crt.sh database')
        for result in cursor.fetchall():
            if len(result) == 1:
                subdomains_list.add(''.join(result))

    # Get subdomains from virustotal
    url = f'https://www.virustotal.com/ui/domains/{target}/subdomains?limit=40'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Connection': 'keep-alive',
                   'Upgrade-Insecure-Requests': '1',
                   'Cache-Control': 'max-age=0'}
        resp, _ = Get(url, headers=headers)
        vt_subdomains_list = [resp.json()['data'][ind]['id'] for ind in range(40)]
        subdomains_list.update(set(vt_subdomains_list))
    except Exception as e:
        logging.error(e)

    # Find all the sites that have the same SSL certificate
    cert = get_cert(target, 443)
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)

    for ind in range(x509.get_extension_count()):
        ext = x509.get_extension(ind)
        if ext.get_short_name() == b'subjectAltName':
            subdomains_list.update(set([x.split('DNS:')[1].strip() for x in ext.__str__().split(',')]))

    return sorted(subdomains_list)
