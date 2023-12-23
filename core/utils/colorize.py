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

COLORS = (
    'Black', 'Maroon', 'Green', 'Olive', 'Navy', 'NULL', 'Teal', 'Silver', 'Grey', 'Red', 'Lime', 'Yellow', 'Blue',
    'Fuchsia', 'Aqua', 'White', 'Grey0', 'NavyBlue', 'DarkBlue', 'NULL', 'Blue3', 'Blue1', 'DarkGreen', 'NULL', 'NULL',
    'DeepSkyBlue4', 'DodgerBlue3', 'DodgerBlue2', 'Green4', 'SpringGreen4', 'Turquoise4', 'NULL', 'DeepSkyBlue3',
    'DodgerBlue1', 'NULL', 'NULL', 'DarkCyan', 'LightSeaGreen', 'DeepSkyBlue2', 'DeepSkyBlue1', 'Green3',
    'SpringGreen3',
    'NULL', 'Cyan3', 'DarkTurquoise', 'Turquoise2', 'Green1', 'SpringGreen2', 'SpringGreen1', 'MediumSpringGreen',
    'Cyan2',
    'Cyan1', 'NULL', 'NULL', 'NULL', 'Purple4', 'Purple3', 'BlueViolet', 'NULL', 'Grey37', 'MediumPurple4', 'NULL',
    'SlateBlue3', 'RoyalBlue1', 'Chartreuse4', 'NULL', 'PaleTurquoise4', 'SteelBlue', 'SteelBlue3', 'CornflowerBlue',
    'NULL', 'DarkSeaGreen4', 'NULL', 'CadetBlue', 'SkyBlue3', 'NULL', 'Chartreuse3', 'NULL', 'SeaGreen3', 'Aquamarine3',
    'MediumTurquoise', 'SteelBlue1', 'NULL', 'SeaGreen2', 'NULL', 'SeaGreen1', 'NULL', 'DarkSlateGray2', 'DarkRed',
    'NULL',
    'NULL', 'DarkMagenta', 'NULL', 'NULL', 'Orange4', 'LightPink4', 'Plum4', 'NULL', 'MediumPurple3', 'SlateBlue1',
    'NULL',
    'Wheat4', 'Grey53', 'LightSlateGrey', 'MediumPurple', 'LightSlateBlue', 'Yellow4', 'NULL', 'DarkSeaGreen', 'NULL',
    'LightSkyBlue3', 'SkyBlue2', 'Chartreuse2', 'NULL', 'PaleGreen3', 'NULL', 'DarkSlateGray3', 'SkyBlue1',
    'Chartreuse1',
    'NULL', 'LightGreen', 'NULL', 'Aquamarine1', 'DarkSlateGray1', 'NULL', 'DeepPink4', 'MediumVioletRed', 'NULL',
    'DarkViolet', 'Purple', 'NULL', 'NULL', 'NULL', 'MediumOrchid3', 'MediumOrchid', 'NULL', 'DarkGoldenrod', 'NULL',
    'RosyBrown', 'Grey63', 'MediumPurple2', 'MediumPurple1', 'NULL', 'DarkKhaki', 'NavajoWhite3', 'Grey69',
    'LightSteelBlue3', 'LightSteelBlue', 'NULL', 'DarkOliveGreen3', 'DarkSeaGreen3', 'NULL', 'LightCyan3',
    'LightSkyBlue1',
    'GreenYellow', 'DarkOliveGreen2', 'PaleGreen1', 'DarkSeaGreen2', 'NULL', 'PaleTurquoise1', 'Red3', 'NULL',
    'DeepPink3',
    'NULL', 'Magenta3', 'NULL', 'DarkOrange3', 'IndianRed', 'HotPink3', 'HotPink2', 'Orchid', 'NULL', 'Orange3',
    'LightSalmon3', 'LightPink3', 'Pink3', 'Plum3', 'Violet', 'Gold3', 'LightGoldenrod3', 'Tan', 'MistyRose3',
    'Thistle3',
    'Plum2', 'Yellow3', 'Khaki3', 'NULL', 'LightYellow3', 'Grey84', 'LightSteelBlue1', 'Yellow2', 'NULL',
    'DarkOliveGreen1',
    'DarkSeaGreen1', 'Honeydew2', 'LightCyan1', 'Red1', 'DeepPink2', 'NULL', 'DeepPink1', 'Magenta2', 'Magenta1',
    'OrangeRed1', 'NULL', 'IndianRed1', 'NULL', 'HotPink', 'MediumOrchid1', 'DarkOrange', 'Salmon1', 'LightCoral',
    'PaleVioletRed1', 'Orchid2', 'Orchid1', 'Orange1', 'SandyBrown', 'LightSalmon1', 'LightPink1', 'Pink1', 'Plum1',
    'Gold1', 'NULL', 'LightGoldenrod2', 'NavajoWhite1', 'MistyRose1')

ATTRS = {"end": "\u001b[0m",
         "start": "\u001b", "type": {"blink": "\u001b[5m", "bold": "\u001b[1m", "underline": "\u001b[4m"}}


def c(string, fg=None, bg=None, attrs=None):
    """Prepare the string to be printed with the colors and types specified"""
    colored = ""
    try:
        if attrs:
            for a in attrs:
                colored = colored + ATTRS["type"][a]

        if fg or bg:
            colored = colored + ATTRS["start"] + "["
            if fg:
                colored = colored + "38;5;" + str(COLORS.index(fg))
            if bg:
                colored = colored + "48;5;" + str(COLORS.index(bg))
            colored = colored + "m"
        colored = colored + str(string) + ATTRS["end"]
    except ValueError:
        return string
    return colored


def printc(string, fg="", bg="", attrs=[]):
    """print the string with the colors and types specified"""
    print(c(string, fg=fg, bg=bg, attrs=attrs))


def list_colors():
    for color in COLORS:
        printc(color, bg=color)
