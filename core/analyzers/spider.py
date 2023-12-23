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
import re
from queue import Queue
from threading import Thread
from urllib.parse import urlparse

from lxml import html

from core.analyzers.parser import parse_forms, parse_robots_txt
from core.utils.colorize import c
from core.utils.network import Get
from core.utils.url_tools import url_check, queries_check

try:
    from BeautifulSoup import BeautifulSoup as bs
except ImportError:
    from bs4 import BeautifulSoup as bs

COMMON_EXT = (
    '.7z', '.aac', '.aiff', '.au', '.avi', '.bin', '.bmp', '.cab', '.dll', '.dmp', '.ear', '.exe', '.flv', '.gif',
    '.gz', '.image', '.iso', '.jar', '.jpeg', '.jpg', '.mkv', '.mov', '.mp3', '.mp4', '.mpeg', '.mpg', '.pdf', '.png',
    '.ps', '.rar', '.scm', '.so', '.tar', '.tif', '.war', '.wav', '.wmv', '.zip'
)
queue = Queue()


def run_as_thread():
    while True:
        link = queue.get()
        Spider.crawl(link)
        queue.task_done()


def create_threads(threads_number):
    for _ in range(threads_number):
        thread = Thread(target=run_as_thread)
        thread.daemon = True
        thread.start()


def add_job_to_queue(job_list):
    for job in job_list:
        queue.put(job)
    queue.join()


class Spider:
    project = {}
    forms = []
    queries_hashes = set()

    def __init__(self, project):
        Spider.project = project

    @staticmethod
    def crawl(link):
        Spider.project['queue'].discard(link)

        # Prevent logout if the user set a Cookies
        if 'logout' in link:
            return

        if link.endswith(COMMON_EXT):
            Spider.project['files'].add(link)

        elif link not in Spider.project['links'].keys():

            resp, err = Get(link, headers=Spider.project['headers'], cookies=Spider.project['cookies'])

            if err:
                return

            # Add the link to the project links
            Spider.project['links'][link] = resp.status_code

            # if link have queries add the link to the queries list
            parsed_link = urlparse(link)
            if parsed_link.query:
                if queries_check(link, Spider.project['base_url'], Spider.queries_hashes):
                    Spider.project['queries'].add(link)

            # Check if the link contain any contents
            if not resp.content:
                return

            # using 'lxml' for best performance
            try:
                soup = bs(resp.content.decode('utf-8'), 'lxml')
            except UnicodeDecodeError as e:
                soup = bs(resp.content, 'lxml')
            except Exception as e:
                logging.error('failed to creating the page soup.')
                return

            # Parse the forms
            forms = parse_forms(soup, link, Spider.project['base_url'])
            if forms:
                Spider.project['forms'] += forms

            trap = re.search('.*(/.*calendar.*)', link) or re.search('^.*?(/.+?/).*?(\1).*(\1)', link)
            if not trap:
                # Parse URls from the page contents
                for tag in soup.findAll('a', href=True):
                    url = url_check(tag['href'].split('#')[0], Spider.project['base_url'])
                    if url:
                        Spider.project['queue'].add(url)
                for tag in soup.findAll(['frame', 'iframe'], src=True):
                    url = url_check(tag['src'].split('#')[0], Spider.project['base_url'])
                    if url:
                        Spider.project['queue'].add(url)
                for tag in soup.findAll('button', formaction=True):
                    url = url_check(tag['formaction'], Spider.project['base_url'])
                    if url:
                        Spider.project['queue'].add(url)

    @staticmethod
    def crawl_robots_txt():
        links = []
        robots_dict = parse_robots_txt(Spider.project['base_url'], Spider.project['base_url'])
        if robots_dict:
            for xml_link in robots_dict['Sitemap']:
                if xml_link.endswith('.xml'):

                    resp, err = Get(xml_link, headers=Spider.project['headers'], cookies=Spider.project['cookies'])
                    if err:
                        continue

                    if resp.content != '':
                        try:
                            tree = html.fromstring(resp.content)
                            links = links + tree.xpath('.//loc/text()')
                        except Exception as e:
                            continue
            links = [url_check(str(link), Spider.project['base_url']) for link in links if
                     link not in Spider.project['links'].keys()]
            links = filter(None, links)
            Spider.project['queue'].update(set(links))
            Spider.project['queue'].update(robots_dict['Allow'])
            Spider.project['queue'].update(robots_dict['Disallow'])
            Spider.project['queue'].update(robots_dict['Noindex'])

    @staticmethod
    def run():
        create_threads(Spider.project['threads_number'])
        while len(Spider.project['queue']) > 0:
            print(c('\r[+]', 'DeepSkyBlue3'), 'Found links: ' + str(len(Spider.project['links'])), end='')
            add_job_to_queue(Spider.project['queue'].copy())
