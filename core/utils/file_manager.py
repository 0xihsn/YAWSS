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

import os

import yaml

from core.utils.colorize import printc

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def load_scan(scan_path):
    if not os.path.isfile(scan_path):
        return "Not found", None
    with open(scan_path, 'r') as stream:
        scan = yaml.load(stream, Loader)
    return "Scan config loaded.", scan


def save_project(project):
    with open("projects/" + project["name"] + ".yml", 'w') as stream:
        yaml.dump(project, stream, Dumper)
    return "Project saved."


def load_project(project):
    if not os.path.isfile("projects/" + project["name"] + ".yml"):
        with open("projects/" + project["name"] + ".yml", 'w') as stream:
            yaml.dump(project, stream, Dumper)
        return "New project created.", project

    with open("projects/" + project["name"] + ".yml", 'r') as stream:
        project = yaml.load(stream, Loader)
    return "Project loaded.", project


def load_module(module_path):
    if not os.path.isfile(module_path):
        return None

    with open(module_path, 'r') as stream:
        config = yaml.load(stream, Loader)
    return "Module loaded.", config


def save_module(module_path, module_contents):
    if not os.path.isfile(module_path):
        with open(module_path, 'w') as stream:
            yaml.dump(module_contents, stream, Dumper)
        return "Config saved."
    else:
        return "This config has been previously saved"


def load_file_as_strings_list(path):
    if os.path.isfile(path):
        with open(path, 'r') as f:
            strings_list = f.read().split("\n")
        return strings_list
    else:
        printc("[!] Your attack file contain incorrect path.", "Red")
        return []
