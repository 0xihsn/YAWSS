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

import itertools
import logging
import os
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from core.utils.cli_arts import process_icon
from core.utils.colorize import c, printc
from core.utils.file_manager import load_file_as_strings_list, load_module, save_project
from core.utils.network import Get, Post, send_raw_request
from core.utils.url_tools import url_check


class AnalysisEngine:
    project = {}
    modules_dir = None
    modules = 'ALL'
    req_timout = 5

    def __init__(self, project, modules=None):
        if modules is None or modules == 'ALL':
            modules = ['ALL', ]
        self.modules_dir = os.getcwd() + '/modules/'
        self.modules = modules
        self.project = project
        project['headers']['Pentest'] = 'YAWSS Analysis Engine'

    def start(self):
        try:
            if 'ALL' in self.modules:
                for filename in os.listdir(self.modules_dir):
                    if filename.endswith('.yml') and filename != 'template.yml':
                        msg, module = load_module(self.modules_dir + filename)
                        print(process_icon, module['name'], 'Analyze started.')
                        self.req_timout = int(module.get('delay', 2)) + 3
                        self.run(module)
                        print(c('[*]', 'Green', attrs=['bold']), module['name'], 'Analyze done!')
                        print(c('[*]', 'Green', attrs=['bold']),
                              c(len(self.project['vulnerabilities'][module['severity']].get(module['name'], [])),
                                'Red', attrs=['bold']),
                              module['name'], 'Found!')

            else:
                for filename in self.modules:
                    msg, module = load_module(self.modules_dir + filename + '.yml')
                    print(process_icon, module['name'], 'Analyze started.')
                    self.req_timout = int(module.get('delay', 2)) + 3
                    self.run(module)
                    print(c('[*]', 'Green', attrs=['bold']), module['name'], 'Analyze done!   \t')
                    print(process_icon,
                          c(len(self.project['vulnerabilities'][module['severity']].get(module['name'], [])),
                            'Red', attrs=['bold']),
                          module['name'], 'Found!')
        except KeyError as e:
            printc(f'[!] Invalid Module format, please check the template. {e}', 'Red', attrs=['bold'])
            logging.error(f'The module contain unsupported key {e}')
        except TypeError as e:
            printc(f'[!] Module not found please check the modules names.', 'Red', attrs=['bold'])
            logging.error(f'Module not found please check the modules names. {e}')

    def run(self, module):
        """ This function gets the module info as dict object and start the module by parse
        the inputs and send requests to the module vectors.
        No return, the results are stored in the project dict."""

        if module['module_type'] == 'check':
            printc('Module type not supported yet.', 'Blue', attrs=['bold'])
            for element in module['check']['contain']:
                # TODO
                pass
            for element in module['check']['does_not_contain']:
                # TODO
                pass
            return

        if module['module_type'] == 'input_output':
            # Load the input to a dictionary
            inputs = {}
            outputs = None
            for num in range(module['input_number']):
                inputs[num] = list(itertools.chain.from_iterable(
                    [load_file_as_strings_list(path) for path in module['input_' + str(num)]])) \
                    if module['input_type'][num] == 'files' else module['input_' + str(num)]
                if not inputs[num]:
                    return
            if len(inputs[0]) > 10:
                printc(
                    '[!] This process may take a long time you have {} input need to be checked with every possible '
                    'entry point'.format(
                        len(inputs[0]) * module['input_number']),
                    'LightSalmon3')

            if module.get('output', None) is not None:
                outputs = list(itertools.chain.from_iterable(
                    [load_file_as_strings_list(path) for path in module['output']])) \
                    if module['output_type'] == 'files' else module['output']
            if module['entry_points'] == 'ALL':
                self.queries_names_test(module, inputs, outputs)
                self.forms_inp_names_test(module, inputs, outputs)
                self.requests_headers_names_test(module, inputs, outputs)
                self.raw_requests_test(module, inputs, outputs)
                self.paths_test(module, inputs, outputs)
            else:
                if module['entry_points'].get('queries_names') is not None:
                    self.queries_names_test(module, inputs, outputs)

                if module['entry_points'].get('forms_inputs_names') is not None:
                    self.forms_inp_names_test(module, inputs, outputs)

                if module['entry_points'].get('requests_headers_names') is not None:
                    self.requests_headers_names_test(module, inputs, outputs)

                if module['entry_points'].get('raw_requests') is not None:
                    self.raw_requests_test(module, inputs, outputs)

                if module['entry_points'].get('paths') is not None:
                    self.paths_test(module, inputs, outputs)

    def analyze_the_output(self, module, resp, inp, mod_vector, outputs):
        """Gets the info about the module and the output as parameters and analyze the output
        to find if the module is success.
        Return Boolean value."""
        vuln = False

        if module['output_path'] != 'SAME':
            resp = Get(url_check(module['output_path'], urlparse(self.project['base_url'])),
                       headers=self.project['headers'], timeout=self.req_timout, cookies=self.project['cookies'])

        if module['output_type'] == 'DELAY':
            if module['delay'] + 3 >= resp.elapsed.total_seconds() >= module['delay']:
                vuln = True

        if module['output_type'] == 'REFLECT':
            outputs = inp if isinstance(inp, list) else [inp]
            if not outputs:
                printc('[!] This output type is not supported for the module entry points', 'Red', attrs=['bold'])
                return None

        if resp and 'response_contents' in module['output_points']:
            if any(output in str(resp.content) for output in outputs):
                vuln = True

        if resp and 'response_headers_names' in module['output_points']:
            if set(outputs) & set(resp.headers.keys()):
                vuln = True
        if resp and 'response_headers_values' in module['output_points']:
            if set(outputs) & set(resp.headers.values()):
                vuln = True
        if resp and 'status_codes' in module['output_points']:
            if resp.status_code in outputs:
                vuln = True

        if vuln:
            if mod_vector not in self.project['vulnerabilities'][module['severity']].get(module['name'], []):
                self.project['vulnerabilities'][module['severity']][module['name']] = self.project['vulnerabilities'][
                                                                                          module['severity']].get(
                    module['name'], []) + [mod_vector]
            save_project(self.project)
        print(process_icon,
              c(len(self.project['vulnerabilities'][module['severity']].get(module['name'], [])),
                'Red', attrs=['bold']),
              module['name'].replace('_', ' ') + '\'s',
              'Detected.\r',
              end='')
        # print(c('\r[+]', 'Blue', attrs=['bold']),
        #       'Checking',
        #       c(next(iter(mod_vector.values())) if isinstance(mod_vector, dict) else mod_vector, 'DarkOrange3'),
        #       end='')
        return vuln

    def queries_names_test(self, module, payloads, outputs):
        """Test if the queries are vulnerable"""
        print(process_icon, 'Analyzing the URL\'s queries.')
        for url in self.project['queries']:
            parsed_url = urlparse(url)
            url_parts = list(parsed_url)
            query = dict(parse_qsl(parsed_url.query))
            query_names = module['entry_points']['queries_names'] if module['entry_points'][
                'queries_names'] else query.keys()
            if module['entry_points']['queries_names'] and isinstance(query_names[0], list):
                mod_url = ''
                for query_names_list in query_names:
                    if len(set(query_names_list).intersection(set(query.keys()))) == len(query_names_list):
                        for inp_index in range(len(payloads[0])):
                            mod_queries = query.copy()
                            inp = []
                            for n, query_name in enumerate(query_names_list):
                                inp.append(payloads[n][inp_index])
                                mod_queries[query_name] = payloads[n][inp_index]
                                url_parts[4] = urlencode(mod_queries)
                                mod_url = urlunparse(url_parts)

                            resp, _ = Get(mod_url, headers=self.project['headers'],
                                          cookies=self.project['cookies'],
                                          timeout=self.req_timout)
                            vulnerable = self.analyze_the_output(module, resp, inp, mod_url, outputs)
                            if vulnerable or vulnerable is None:
                                break
            else:
                for query_name in query_names:
                    if query_name in query.keys():
                        for inp in payloads[0]:
                            mod_queries = query.copy()
                            mod_queries[query_name] = inp
                            url_parts[4] = urlencode(mod_queries)
                            mod_url = urlunparse(url_parts)
                            resp, _ = Get(mod_url, headers=self.project['headers'],
                                          cookies=self.project['cookies'],
                                          timeout=self.req_timout)
                            vulnerable = self.analyze_the_output(module, resp, inp, mod_url, outputs)
                            if vulnerable or vulnerable is None:
                                break

    def forms_inp_names_test(self, module, payloads, outputs):
        """Test if the form inputs are vulnerable"""
        print(process_icon, 'Analyzing the Forms Inputs.')
        for form in self.project['forms']:
            forms_inputs_names = module['entry_points'].get('forms_inputs_names')
            data = {}
            for form_input in form['inputs']:
                if form_input.get('name'):
                    data[form_input.get('name')] = form_input.get('value', None)

            if module['entry_points']['forms_inputs_names'] and isinstance(forms_inputs_names[0], list):
                for form_input_list in forms_inputs_names:
                    for payload_index in range(len(payloads[0])):
                        mod_data = data.copy()
                        passed = True
                        inp = []
                        for n, form_input in enumerate(form_input_list):
                            inp.append(payloads[n][payload_index])
                            if form_input not in mod_data.keys():
                                passed = False
                                break
                            mod_data[form_input] = payloads[n][payload_index]
                        if passed:
                            if form['method'] == 'post':
                                resp, _ = Post(form['action'], data=data, headers=self.project['headers'])
                            else:
                                resp, _ = Get(form['action'], params=data, timeout=self.req_timout)
                            vulnerable = self.analyze_the_output(module, resp, inp, {form['action']: mod_data}, outputs)
                            if vulnerable or vulnerable is None:
                                break
            else:
                for form_input in form['inputs']:
                    if form_input['type'] == 'hidden' and not module['test_hidden_form_inputs']:
                        continue
                    for payload in payloads[0]:
                        mod_data = data.copy()
                        mod_data[form_input['name']] = payload
                        if form['method'] == 'post':
                            resp, _ = Post(form['action'], data=data, headers=self.project['headers'])
                        else:
                            url = list(urlparse(form['action']))
                            url[4] = urlencode(mod_data)
                            resp, _ = Get(urlunparse(url), timeout=self.req_timout)
                        vulnerable = self.analyze_the_output(module, resp, payload,
                                                             {form['action']: mod_data, 'method': form['method']},
                                                             outputs)
                        if vulnerable or vulnerable is None:
                            break

    def requests_headers_names_test(self, module, payloads, outputs):
        """Test if the request headers are vulnerable"""
        print(process_icon, 'Analyzing the requests headers.')
        requests_headers_names = module['entry_points']['requests_headers_names'] if module['entry_points'][
            'requests_headers_names'] else self.project['headers'].keys()
        for link in self.project['links']:
            if module['entry_points']['requests_headers_names'] and isinstance(requests_headers_names[0], list):
                for headers_names_list in requests_headers_names:
                    for payload_index in range(len(payloads[0])):
                        headers = self.project['headers'].copy()
                        inp = []
                        for n, name in enumerate(headers_names_list):
                            inp.append(payloads[n][payload_index])
                            headers[name] = payloads[n][payload_index]
                        resp, _ = Get(link, headers=headers, timeout=self.req_timout)
                        vulnerable = self.analyze_the_output(module, resp, inp, {link: headers}, outputs)
                        if vulnerable or vulnerable is None:
                            break

            else:
                for name in requests_headers_names:
                    for inp in payloads[0]:
                        if name == 'Pentest':
                            continue
                        headers = self.project['headers'].copy()
                        headers[name] = inp
                        resp, _ = Get(link, headers=headers, timeout=self.req_timout)
                        vulnerable = self.analyze_the_output(module, resp, inp, {link: headers}, outputs)
                        if vulnerable or vulnerable is None:
                            break

    def raw_requests_test(self, module, raw_requests, outputs):
        """Send raw request to the host and analyze the output points."""
        print(process_icon, 'Analyzing the server respond for the requests.')
        host = urlparse(self.project['base_url']).hostname
        for raw_request in raw_requests[0]:
            raw_request = raw_request.replace('\\n', '\n').replace('\\r', '\r')
            resp, _ = send_raw_request(host, raw_request)
            if resp:
                if self.analyze_the_output(module, resp, None, raw_request, outputs) is None:
                    break

    def paths_test(self, module, payloads, outputs):
        """Send get request to the path and analyze the output points
           input parameter must be a in this form {0: ['path1','path2']}"""
        print(process_icon, 'Analyzing the paths.')
        for payload in payloads[0]:
            url = url_check(payload, self.project['base_url'])
            resp, _ = Get(url, headers=self.project['headers'], timeout=self.req_timout)
            if self.analyze_the_output(module, resp, payload, {url: payload}, outputs) is None:
                return
