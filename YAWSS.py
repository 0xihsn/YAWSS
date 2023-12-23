"""

    ▓██   ██▓ ▄▄▄       █     █░  ██████   ██████
     ▒██  ██▒▒████▄    ▓█░ █ ░█░▒██    ▒ ▒██    ▒
      ▒██ ██░▒██  ▀█▄  ▒█░ █ ░█ ░ ▓██▄   ░ ▓██▄
      ░ ▐██▓░░██▄▄▄▄██ ░█░ █ ░█   ▒   ██▒  ▒   ██▒
      ░ ██▒▓░ ▓█   ▓██▒░░██▒██▓ ▒██████▒▒▒██████▒▒
       ██▒▒▒  ▒▒   ▓▒█░░ ▓░▒ ▒  ▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░
     ▓██ ░▒░   ▒   ▒▒ ░  ▒ ░by: ihsan b. | ihsn.me
     ▒ ▒ ░░    ░   ▒     ░   ░  ░  ░  ░  ░  ░  ░
     ░ ░           ░  ░    ░          ░        ░
     ░ ░

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

import argparse
import logging
import random
import sys

from UI.YAWSS_cli import yawss_cli
from UI.YAWSS_web.app import start_the_web_ui
from core.utils.cli_arts import BANNERS
from core.utils.colorize import printc


def start():
    try:
        # Print the banner
        print(BANNERS[random.randint(0, len(BANNERS) - 1)])
        # configure the logs
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            filename=None
        )
        file_handler = logging.FileHandler('logs/log', 'w')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        log = logging.getLogger()
        for h in log.handlers:
            log.removeHandler(h)
        log.addHandler(file_handler)

        # Get the arguments from the console
        parser = argparse.ArgumentParser("YAWSS")
        parser.add_argument("-ui", "--user-interface", help="Set the preferred UI: cli, web",
                            type=str, default='cli')
        parser.add_argument("-s", "--scan", help="The scan yaml config file path (required if you are using the cli)",
                            type=str)
        parser.add_argument("-m", "--modules",
                            help="Set the modules by writing the names without extensions"
                                 " (Leave empty or set to ALL for using all the modules). EX: -m xss,sql",
                            type=str)
        parser.add_argument("--host", help="Web UI host (can be used just with web UI)",
                            type=str)
        parser.add_argument("--port", help="Web UI port (can be used just with web UI)",
                            type=int)

        args = parser.parse_args()

        if args.user_interface == 'web':
            # disable the printing to console
            with open('logs/console', "w") as logger:
                host = args.host if args.host else '127.0.0.1'
                port = args.port if args.port else 5000
                printc(f'YAWSS server started at {host}:{port}', "DarkSeaGreen")
                sys.stdout = logger
                start_the_web_ui(host=host, port=port)

        elif args.user_interface == 'cli':
            modules = args.modules.split(",") if args.modules else None
            if args.scan:
                yawss_cli(args.scan, modules)
            else:
                printc("Please enter the scan path!", "Red", attrs=["bold"])
        else:
            printc("Sorry! for now we just support two type of UI's: web and cli.", "Red", attrs=["bold"])
    except KeyboardInterrupt as e:
        printc('[X] Ok ok, quitting.', 'Red', attrs=['bold'])
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    start()
