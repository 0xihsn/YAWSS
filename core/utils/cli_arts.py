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

from core.utils.colorize import c

BANNERS = [
    c('''
        ▓██   ██▓ ▄▄▄       █     █░  ██████   ██████ 
         ▒██  ██▒▒████▄    ▓█░ █ ░█░▒██    ▒ ▒██    ▒ 
          ▒██ ██░▒██  ▀█▄  ▒█░ █ ░█ ░ ▓██▄   ░ ▓██▄   
          ░ ▐██▓░░██▄▄▄▄██ ░█░ █ ░█   ▒   ██▒  ▒   ██▒
          ░ ██▒▓░ ▓█   ▓██▒░░██▒██▓ ▒██████▒▒▒██████▒▒
           ██▒▒▒  ▒▒   ▓▒█░░ ▓░▒ ▒  ▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░
         ▓██ ░▒░   ▒   ▒▒ ░  ▒ ░''', 'PaleTurquoise4') + c("by: ihsan b. | ihsn.me", 'DeepSkyBlue4') + c('''
         ▒ ▒ ░░    ░   ▒     ░   ░  ░  ░  ░  ░  ░  ░  
         ░ ░           ░  ░    ░          ░        ░  
         ░ ░                    
    ''', 'PaleTurquoise4'),
    c('''
    YAWSS                                   by: ihsan b. | ihsn.me''', 'Orange3') +
    c(''' 
                  _
                 | |
                 | |===( )   //////
                 |_|   |||  | o o|
                        ||| ( c  )                  ____
                         ||| \\= /                  ||   \\_
                          ||||||                   ||     |
                          ||||||                ...||__/|-"
                          ||||||             __|________|__
                            |||             |______________|
                            |||             || ||      || ||
                            |||             || ||      || ||
    ------------------------|||-------------||-||------||-||-------
                            |__>            || ||      || ||
    ''', 'DarkOrange3'),
    c('''
    YY   YY   AAA   WW      WW  SSSSS   SSSSS  
    YY   YY  AAAAA  WW      WW SS      SS      
     YYYYY  AA   AA WW   W  WW  SSSSS   SSSSS  
      YYY   AAAAAAA  WW WWW WW      SS      SS 
      YYY   AA   AA   WW   WW   SSSSS   SSSSS\n''', 'MediumPurple4') +
    c('''
                        by: ihsan b. | ihsn.me
    ''', 'SlateBlue3'),
    c('''
    XYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSX
    M""MMMM""M MMP"""""""MM M""MMM""MMM""M MP""""""`MM MP""""""`MM 
    M. `MM' .M M' .mmmm  MM M  MMM  MMM  M M  mmmmm..M M  mmmmm..M 
    MM.    .MM M         `M M  MMP  MMP  M M.      `YM M.      `YM 
    MMMb  dMMM M  MMMMM  MM M  MM'  MM' .M MMMMMMM.  M MMMMMMM.  M 
    MMMM  MMMM M  MMMMM  MM M  `' . '' .MM M. .MMM'  M M. .MMM'  M 
    MMMM  MMMM M  MMMMM  MM M    .d  .dMMM Mb.     .dM Mb.     .dM 
    XYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSYAWSSX
    ''', 'LightSeaGreen') +
    c('''                                        by: ihsan b. | ihsn.me
    ''', 'PaleTurquoise4')
]

error_icon = '''
\t\t.-----------------------. 
\t\t| .---------------------. |
\t\t| |             __      | |
\t\t| |      _    .' _|     | |
\t\t| |     (_)   | |       | |
\t\t| |      _    | |       | |
\t\t| |     (_)   | |_      | |
\t\t| |           `.__|     | |
\t\t| |                     | |
\t\t| '---------------------' |
\t\t '-----------------------' 
'''

process_icon = c('[+]', 'DarkCyan', attrs=['bold'])
