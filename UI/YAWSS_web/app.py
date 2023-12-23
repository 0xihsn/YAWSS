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
import json
import logging
import multiprocessing
import os

# Flask packages
import yaml
from flask import Flask, render_template, request

from core.analyzers.engine import AnalysisEngine
from core.analyzers.spider import Spider
from core.analyzers.subdomains import get_subdomains
from core.utils.file_manager import load_scan, load_project, save_project
from core.utils.network import Get

# YAWSS scripts

root_path = os.path.dirname(os.path.realpath(__file__))

app = Flask('YAWSS',
            root_path=root_path)

app.config.update(
    SECRET_KEY=os.urandom(24),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_NAME='YAWSS',
    WTF_CSRF_TIME_LIMIT=None
)

scans_processes = {}


def scan_target(name, modules):
    # Start a new project
    scan_path = f'scans/{name}.yml'
    msg, project = load_scan(scan_path)
    if not project:
        logging.error('Scan config not found.')
        return
    resp, err = Get(project['base_url'], headers=project['headers'], cookies=project['cookies'])
    if err:
        logging.error('[!] Host can not be reached')
        return
    project['queue'].add(project['base_url'])
    try:
        msg, project = load_project(project)
        logging.info(msg)
        if project.get('done', False):
            return
        project['done'] = False
        if project['enable_crawler']:
            logging.info('Parsing robots.txt file.')
            Spider(project).crawl_robots_txt()
            logging.info('Start Crawling.')
            logging.info('The spiders are Just Doing Their Best.')
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
            logging.info('Crawling DONE!')
        if project['subdomains_research']:
            logging.info('Subdomain research started.')
            project['subdomains'] = get_subdomains(project['base_url'])
            logging.info('Subdomain research done!')
        save_project(project)
        logging.info('Analysis Engine started.')
        AnalysisEngine(project, modules).start()
        project['done'] = True
        save_project(project)
    except KeyboardInterrupt as e:
        logging.error(f'Terminated by user, {e}')
        save_project(project)
    except KeyError as e:
        logging.error(f'Invalid project please check the template and try again, {e}')
    except Exception as e:
        logging.error(e)
        save_project(project)


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


@app.route('/data', methods=['POST'])
def data():
    name = request.form.get('name')
    scan_path = f'projects/{name}.yml'
    msg, res = load_scan(scan_path)
    return json.dumps(res, default=set_default)


@app.route('/add_scan', methods=['POST'])
def add_scan():
    scan = request.files.get('scan')
    try:
        if yaml.load(scan):
            if os.path.isfile('scans/' + scan.filename):
                return 'This scan config is already exist.'
            else:
                scan.save('scans/' + scan.filename)
                return 'Scan config imported successfully.'
        return 'Please be sure that your YAML file is not empty'
    except Exception as e:
        return 'Please be sure that your files type is YAML'


@app.route('/add_module', methods=['POST'])
def add_module():
    module = request.files.get('module')
    try:
        if yaml.load(module):
            if os.path.isfile('modules/' + module.filename):
                return 'This module is already exist.'
            else:
                module.save('modules/' + module.filename)
                return 'module config imported successfully.'
        return 'Please be sure that your YAML file is not empty'
    except Exception as e:
        return 'Please be sure that your files type is YAML'


@app.route('/start_scan', methods=['POST'])
def start_scan():
    if len(scans_processes.keys()) == 5:
        return 'You can start only 5 scans simultaneously.'
    name = request.form.get('name')
    modules = request.form.get('modules')
    modules = modules.split(',')
    if name not in scans_processes.keys():
        scans_processes[name] = multiprocessing.Process(target=scan_target, args=(name, modules))
        scans_processes[name].daemon = True
        scans_processes[name].start()
        return f'"{name}" Scan Started!'
    return 'The scan is active!'


@app.route('/cancel_scan', methods=['POST'])
def cancel_scan():
    name = request.form.get('name')
    if scans_processes.get(name):
        scans_processes.get(name).terminate()
        scans_processes.pop(name, None)
        return 'Scan Stoped!'
    return 'Scan not found.'


@app.route('/get_scans_and_modules_names')
def get_scans_and_modules_names():
    data = {'scans': [],
            'modules': []}
    for filename in os.listdir('scans/'):
        if filename.endswith('.yml') and filename != 'template.yml':
            data['scans'].append(filename.split('.')[0])

    for filename in os.listdir('modules/'):
        if filename.endswith('.yml') and filename != 'template.yml':
            data['modules'].append(filename.split('.')[0])

    return json.dumps(data)


def start_the_web_ui(host, port, debug=False):
    app.run(host=host, port=port, debug=debug)
