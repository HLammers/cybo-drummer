''' Cybo-Drummer - Humanize Those Drum Computers!
    https://github.com/HLammers/cybo-drummer
    Copyright (c) 2024 Harm Lammers

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.'''

import machine
from sys import exit
import time

from main_loops import init, main, shut_down

_AVOID_BOOT_PIN = const(2)
_BOOTLOADER_PIN = const(3)

# if trigger button is pressed: avoid the main loop to start
# if both trigger button and page button are pressed: trigger boot loader mode
led = machine.Pin(25, machine.Pin.OUT)
led.on()
boot_pin = machine.Pin(_AVOID_BOOT_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
boot_loader_pin = machine.Pin(_BOOTLOADER_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
start_time = time.ticks_ms()
while time.ticks_diff(time.ticks_ms(), start_time) < 1000:
    if not boot_pin.value():
        print('trigger button pressed')
        if not boot_loader_pin.value():
            machine.bootloader()
        else:
            print('boot interrupted')
            exit()
led.off()
del led
del boot_pin
del boot_loader_pin
init()
try:
    main()
finally:
    shut_down()