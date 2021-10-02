from enum import Enum

class Colors(Enum):
    grey = 30
    red = 31
    green = 32
    yellow = 33
    blue = 34
    magenta = 35
    cyan = 36
    white = 37


class Highlights(Enum):
    on_grey = 40
    on_red = 41
    on_green = 42
    on_yellow = 43
    on_blue = 44
    on_magenta = 45
    on_cyan = 46
    on_white = 47


class Attributes(Enum):
    bold = 1
    dark = 2
    underline = 3
    blink = 4
    reverse = 5
    concealed = 6


RESET = '\033[0m'


def colored(string, color=None, on_color=None, **kargs):
    format_str = '\033[%dm%s'

    if color is not None:
        string = format_str % (color.value, string)
    
    if on_color is not None:
        string = format_str % (on_color.value, string)
    
    if attrs := (kargs.get('attrs', None)) is not None:
        for attr in attrs:
            string = format_str % (attr.value, string)
    
    string += RESET

    return string

def level_logging(string, level, correct=Colors.green, warning=Colors.yellow, error=Colors.red):
    if level == 0:
        return colored(string, correct, attrs=[Attributes.bold])
    elif level == 3:
        return colored(string, warning, attrs=[Attributes.bold])
    elif level == 1:
        return colored(string, error, attrs=[Attributes.bold])
    else:
        return colored(string, Colors.magenta, attrs=[Attributes.bold])


def cprint(string, color, **kargs):
    print(colored(string, color, **kargs))
