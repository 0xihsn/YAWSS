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

import random
import sys
from os import system, name

from core.utils.cli_arts import BANNERS


def clear_screen(banner=False):
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
    # Print the banner
    if banner:
        print(BANNERS[random.randint(0, len(BANNERS) - 1)])


def delete_last_output_line():
    sys.stdout.write("\033[F")  # back to previous line
    sys.stdout.write("\033[K")  # clear line
