
''' console output.
fine under sublime with the following
"build_systems":
    [
        {
            "encoding": "UTF-8",
            "file_regex": "^[ ]*File \"(...*?)\", line ([0-9]*)",
            "name": "Anaconda ansi",
            "selector": "source.python",
            "shell_cmd": "/env/bin/python -u $file",
            "syntax": "Packages/ANSIescape/ANSI.tmLanguage",
            "target": "ansi_color_build"
        },
'''

class AnsiColors:
    # Text attributes
    OFF = '\033[0m'
    BOLD = '\033[1m'
    UNDERSCORE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    CONCEALED = '\033[7m'
    # Foreground colors
    BLACK = '\033[30m'
    LBLACK = '\033[1;30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    # light/pale colors
    LRED = '\033[1;31m'
    LGREEN = '\033[1;32m'
    LYELLOW = '\033[1;33m'
    LBLUE = '\033[1;34m'
    LMAGENTA = '\033[1;35m'
    LCYAN = '\033[1;36m'
    LWHITE = '\033[1;37m'
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[0;41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


if __name__ == '__main__':
    def print_format_table():
        """
        prints table of formatted text format options
        """
        for style in range(8):
            for fg in range(30, 38):
                s1 = ''
                for bg in range(40, 48):
                    format = ';'.join([str(style), str(fg)])
                    s1 += '\033[%sm %s \033[0m' % (format, format)
                print(s1)
            print('\n')

    print_format_table()

    import sys
    c = AnsiColors
    for k, v in c.__dict__.items():
        sys.stdout.write(str(v) + str(k) + ' ')

    print('\033[1;31m;40m RED')
    print(c.OFF)
