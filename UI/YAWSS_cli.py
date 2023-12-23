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
import logging

from core.analyzers.engine import AnalysisEngine
from core.analyzers.spider import Spider
from core.analyzers.subdomains import get_subdomains
from core.utils.cli_arts import error_icon, process_icon
from core.utils.colorize import printc, c
from core.utils.file_manager import save_project, load_project, load_scan
from core.utils.network import Get


def yawss_cli(project_path, modules=None):
    # Start a new project
    msg, project = load_scan(project_path)
    if not project:
        printc('[!] Scan config not found.', 'DeepPink4', attrs=['bold'])
        return

    resp, err = Get(project['base_url'], headers=project['headers'], cookies=project['cookies'])
    if err:
        printc('[!] Host can not be reached', 'Red', attrs=['bold'])
        return
    project['queue'].add(project['base_url'])
    try:
        msg, project = load_project(project)
        printc('[~] ' + msg, 'SteelBlue', attrs=['blink'])
        if project['enable_crawler']:
            print(process_icon, 'Parsing robots.txt file.')
            Spider(project).crawl_robots_txt()
            print(process_icon, 'Start Crawling.')
            printc('[~] The spiders are Just Doing Their Best.', 'Grey69')
            Spider(project).run()
            # Delete the duplicated forms
            forms_hashes = set()
            new_forms = []
            for form in project['forms']:
                form_hash = hashlib.sha1(str(form).encode()).hexdigest()
                if form_hash in forms_hashes:
                    continue
                else:
                    forms_hashes.add(form_hash)
                    new_forms.append(form)
            project['forms'] = new_forms
            del forms_hashes
            print('\n' + process_icon, 'Crawling DONE!')
        if project['subdomains_research']:
            print(process_icon, 'Subdomain research started.')
            project['subdomains'] = get_subdomains(project['base_url'])
            print(process_icon, 'Subdomain research done!')
        nums_color = 'DarkSeaGreen'
        print(process_icon,
              c(f'{len(project["links"])}', nums_color, attrs=['bold']) + ' Links,',
              c(f'{len(project["forms"])}', nums_color, attrs=['bold']) + ' Forms,',
              c(f'{len(project["queries"])}', nums_color, attrs=['bold']) + ' Queries',
              c(f'{len(project["subdomains"])}', nums_color, attrs=['bold']) + ' Subdomains and',
              c(f'{len(project["files"])}', nums_color, attrs=['bold']) + ' Files Found.')
        save_project(project)
        print(process_icon + ' Analysis Engine started.')
        AnalysisEngine(project, modules).start()
        save_project(project)
    except KeyboardInterrupt as e:
        printc('[X] Ok ok, quitting.', 'Red', attrs=['bold'])
        save_project(project)
    except KeyError as e:
        logging.error('Invalid project please check the template and try again')
        print(c('[!]', 'Red'), e, 'value not found')
        printc('Invalid project please check the template and try again', 'Red', attrs=['bold'])
    except Exception as e:
        logging.error(e)
        save_project(project)
        printc(error_icon + '\n\tAn Unexpected Error Occurred! Please check the logs', 'Red', attrs=['bold'])
