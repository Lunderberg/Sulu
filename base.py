#!/usr/bin/env python3

from base64 import b64decode
from gzip import GzipFile
import io
import shutil
import sys
import termios
import tty


class AlternateScreen:
    def __enter__(self):
        print("\0337\033[?47h", end="")
        return self

    def __exit__(self, *args):
        print("\033[2J\033[?47l\0338", end="")


class HideCursor:
    def __enter__(self):
        print("\033[?25l", end="")
        return self

    def __exit__(self, *args):
        print("\033[?25h", end="")


class UnbufferStdin:
    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.prev_settings = None

    def __enter__(self):
        self.prev_settings = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)
        return self

    def __exit__(self, *args):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.prev_settings)


def ansi_print_sequence(data, size=None, skip_last_pixel=True):
    if size is None:
        size = shutil.get_terminal_size()

    header_size = 4
    assert len(data) >= header_size
    data_width = data[1] * 256 + data[0]
    data_height = data[3] * 256 + data[2]

    assert len(data) == header_size + data_width * data_height

    term_width, term_height = size
    for term_i in range(term_height):
        for term_j in range(term_width):
            if (
                not skip_last_pixel
                or term_i + 1 < term_height
                or term_j + 1 < term_width
            ):
                data_i = term_i * data_height // term_height
                data_j = term_j * data_width // term_width
                color_index = data[header_size + data_i * data_width + data_j]
                yield f"\033[48;5;{color_index}m"
                yield " "

    yield "\033[0m"


def main():
    with GzipFile(fileobj=io.BytesIO(b64decode(image_data))) as f:
        data = f.read()

    to_print = "".join(ansi_print_sequence(data))

    with AlternateScreen(), HideCursor(), UnbufferStdin():
        print(to_print, end="")
        sys.stdin.read(1)


image_data = """COLOR_DATA"""

if __name__ == "__main__":
    main()
