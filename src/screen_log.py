''' Screen logger for Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This file is only used in test versions of Cybo-Drummer to be able to create screenshots

    MIT licence:

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'''

if __debug__:
    _log_disabled = False # set to False to enable screen logging
    _row_data = ''

    def toggle_log() -> None:
        global _log_disabled
        _log_disabled ^= True
        with open('screenlog.txt', 'a') as file:
            if _log_disabled:
                file.write('###### logging disabled\n')
            else:
                file.write('###### logging enabled\n')

    def add_marker(text: str) -> None:
        if _log_disabled:
            return
        with open('screenlog.txt', 'a') as file:
            file.write('###### ')
            file.write(text)
            file.write('\n')

    def add_fill_rect(x: int, y: int, w: int, h: int, color: int) -> None:
        if _log_disabled:
            return
        with open('screenlog.txt', 'a') as file:
            file.write(f'fill_rect({x},{y},{w},{h},{color})\n')

    def set_window(x: int, y: int, w: int, h: int) -> None:
        if _log_disabled:
            return
        with open('screenlog.txt', 'a') as file:
            file.write(f'set_window({x},{y},{w},{h})\n')

    def start_window_write(back_color: int, fore_color: int) -> bool:
        if _log_disabled:
            return False
        with open('screenlog.txt', 'a') as file:
            file.write(f'add_window_data({back_color},{fore_color},\n')
        return True

    def add_to_window_row(pixel_set: bool) -> None:
        if _log_disabled:
            return
        global _row_data
        _row_data += str(int(pixel_set))

    def write_window_row() -> None:
        if _log_disabled:
            return
        global _row_data
        with open('screenlog.txt', 'a') as file:
            file.write(f"'{_row_data}'")
            file.write(',\n')
        _row_data = ''

    def finish_window_write() -> None:
        if _log_disabled:
            return
        with open('screenlog.txt', 'a') as file:
            file.write(')\n')