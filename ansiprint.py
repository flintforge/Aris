from ansicolor import AnsiColors as Ansi
from ansicolor import AnsiColors as Ansi


def error(msg):
    print(Ansi.RED, msg, Ansi.OFF)


def warning(msg):
    print(Ansi.LYELLOW, msg, Ansi.OFF)

