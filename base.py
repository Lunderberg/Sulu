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


def get_best_rep(color_indices):
    a, b, c, d = color_indices

    # Sub-character colors are arranged as shown below.
    #
    #  a | d
    #  --+--
    #  b | c

    # All sub-chars are same color
    if a == b == c == d:
        return a, a, " "

    # 3/4 sub-chars are same color, use the blocks with 3/4 quadrants
    # filled in.
    elif a == b == c:
        return a, d, chr(0x2599)
    elif a == c == d:
        return a, b, chr(0x259C)
    elif a == b == d:
        return a, c, chr(0x259B)
    elif b == c == d:
        return b, a, chr(0x259F)

    # 2/4 sub-chars are one color, 2/4 are another.  Use the
    # upper-half, left-half, and the upper-left/bottom-right blocks.
    elif a == d and b == c:
        return a, b, chr(0x2580)
    elif a == b and c == d:
        return a, c, chr(0x258C)
    elif a == c and b == d:
        return a, b, chr(0x259A)

    # The 4 subchars have 3 distinct colors, cannot perfectly
    # reproduce.  So, shrug and use the half blocks here as well.
    elif a == d and b != c:
        return a, b, chr(0x2580)
    elif a == b and c != d:
        return a, c, chr(0x258C)
    elif a == c and b != d:
        return a, b, chr(0x259A)
    elif b == c and a != d:
        return b, d, chr(0x2580)
    elif b == d and a != c:
        return b, c, chr(0x259A)
    elif c == d and b != c:
        return c, b, chr(0x258C)

    # All 4 subchars have different colors.
    elif len(set(color_indices)) == 4:
        return a, b, chr(0x2580)


def ansi_print_sequence(data, size=None, skip_last_pixel=True):
    if size is None:
        size = shutil.get_terminal_size()

    header_size = 4
    assert len(data) >= header_size
    data_width = data[1] * 256 + data[0]
    data_height = data[3] * 256 + data[2]

    assert len(data) == header_size + data_width * data_height

    offsets = [
        (0, 0),
        (0, 1),
        (1, 1),
        (1, 0),
    ]

    term_width, term_height = size
    for term_i in range(term_height):
        for term_j in range(term_width):
            if (
                not skip_last_pixel
                or term_i + 1 < term_height
                or term_j + 1 < term_width
            ):
                color_indices = []
                for offset_i, offset_j in offsets:
                    data_i = (data_height * (2 * term_i + offset_i)) // (
                        term_height * 2
                    )
                    data_j = (data_width * (2 * term_j + offset_j)) // (term_width * 2)
                    color_indices.append(
                        data[header_size + data_i * data_width + data_j]
                    )
                fg_color, bg_color, block_char = get_best_rep(color_indices)
                yield f"\033[38;5;{fg_color};48;5;{bg_color}m{block_char}"
                # yield block_char

    yield "\033[0m"


def main():
    with GzipFile(fileobj=io.BytesIO(b64decode(image_data))) as f:
        data = f.read()

    to_print = "".join(ansi_print_sequence(data))

    with AlternateScreen(), HideCursor(), UnbufferStdin():
        print(to_print, end="")
        sys.stdout.flush()
        sys.stdin.read(1)


image_data = """COLOR_DATA"""

if __name__ == "__main__":
    main()
