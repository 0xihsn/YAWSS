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

from core.utils.network import Get
from core.utils.url_tools import url_check

try:
    from requests import exceptions
except ImportError:

    logging.error('requests library missing. pip install requests')
    raise ImportError('requests library missing. pip install requests')


def parse_forms(soup, link, base_url):
    forms = []

    # Parse forms from the link
    forms_soup = soup.findAll('form')
    if forms_soup is not []:
        for form in forms_soup:
            if form != "" and form is not None:
                form_contents = {}
                form_id = form.attrs.get('id')
                # Get the form action (requested URL)
                action = form.attrs.get("action")
                action = url_check(action, base_url)
                if action is not None:
                    # Get the form method (POST, Get, DELETE, etc) default GET
                    method = form.attrs.get("method", "Get")
                    # Get all form inputs
                    inputs = []
                    for textarea in soup.findAll('textarea'):
                        if textarea.get('form') == form_id:
                            inputs.append({'name': textarea.get('name'),
                                           'type': textarea.get('type') if textarea.get('type') else 'text',
                                           'value': textarea.get('value') if textarea.get('value') else 'YAWSS'})
                    first_check_box = True
                    for data_tag in form.find_all(['input', 'select', 'textarea']):

                        if data_tag.get('type') == 'submit' or data_tag.get('name') == 'Submit-button':
                            continue

                        # Prevent making change in the hidden data values
                        if data_tag.get('type') == 'hidden':
                            inputs.append({'name': data_tag.get('name'),
                                           'type': data_tag.get('type') if data_tag.get('type') else 'text',
                                           'value': data_tag.get('value')})
                        elif data_tag.name == 'select':
                            inputs.append({'name': data_tag.get('name'),
                                           'type': data_tag.get('type') if data_tag.get('type') else 'text',
                                           'value': data_tag.find('option').get('value')})
                        elif data_tag.name == 'textarea':
                            inputs.append({'name': data_tag.get('name'),
                                           'type': data_tag.get('type') if data_tag.get('type') else 'text',
                                           'value': data_tag.get('value') if data_tag.get('value') else 'YAWSS'})
                        else:
                            # Get just the first checkbox value
                            if data_tag.get('type') == 'checkbox':
                                if first_check_box:
                                    first_check_box = False
                                else:
                                    continue

                            inputs.append({'name': data_tag.get('name'),
                                           'type': data_tag.get('type') if data_tag.get('type') else 'text',
                                           'value': data_tag.get('value') if data_tag.get('value') else 'YAWSS'})

                    # put everything to the resulting dictionary
                    form_contents["action"] = action
                    form_contents["method"] = method.lower() if method else None
                    form_contents["inputs"] = inputs
                    # form_contents["link"] = link
                    forms.append(form_contents)
    return forms


def parse_robots_txt(link, base_url):
    result = {
        "Sitemap": set(),
        "User-agent": set(),
        "Disallow": set(),
        "Allow": set(),
        "Noindex": set()
    }

    resp, _ = Get(link + "/robots.txt")
    if resp and resp.status_code == 200:
        try:
            for line in resp.content.decode('utf-8').split('\n'):
                parts = line.split(': ')
                if len(parts) == 2:
                    url = url_check(parts[1].split('#')[0].strip(), base_url)
                    if url:
                        result[parts[0].strip()].add(url)
        except KeyError as e:
            pass
    return result
