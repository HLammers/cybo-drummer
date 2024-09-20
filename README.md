<img src="/logos/colour_logo.svg" width="100%">

# Cybo-Drummer
**Humenize those drum computers!**

(c) 2024 Harm Lammers

> [!IMPORTANT]
> Cybo-Drummer is not yet released. This readme file is work in progress in preparation of releasing Cybo-Drummer to the public. Feel free to come back here to see it grow for the next couple of weeks!
## Introduction
I own an electronic drum kit and a bunch of drum computers and my dream was to use the former to play the latter, so I went searching for a way to do just that – allowing me to easily switch between different configurations combining the sounds of one or more drum computers. I looked for hardware solutions, but couldn’t find any. I looked for software solutions, but I could only find MIDI mappers or other complex solutions that would never give me the easy to use experience I had it mind. It turns out that (as usual) I go against the current fashion of trying to make an electronic drum kit sound (and look) as acoustic as possible. So I decided to develop my own solution – and publish it as open source DIY project, hoping it finds like-minded drummers!
## What Is It?
Cybo-Drummer is a MIDI router/mapper specially designed for mapping drum triggers (electronic drum kits’ brains) to drum computers. Since there is no standard for the MIDI messages sent by drum kits, nor the messages received by drum computers, Cybo-Drummer offers a flexible way of mapping the one to the other.

The idea for the hardware was inspired by the work of [diyelectromusic (Kevin)](https://diyelectromusic.com/), in particular his [Raspberry Pi Pico Multi MIDI Router](https://diyelectromusic.com/2022/09/19/raspberry-pi-pico-multi-midi-router-part-5/). The first prototype is an additional pcb on top of the Multi Midi Router.
### Features
#### Hardware
* 6 times 5-pin DIN MIDI input port: connect up to 6 drumkits, drumpads, keyboards, etc.
* 6 times 5-pin DIN MIDI output port: connect up to 6 drum computers, samplers, synthesizer, etc.
* micro USB port for power and firmware update (MIDI over USB is not yet implemented; next prototype will include 5.5mm socket for 5V DC power supply)
* 2.2 inch colour display (220x176 pixels)
* 2 rotary encoders and 2 push buttons for input and navigation (plus reset button)
#### Mapping
```mermaid
graph LR
    subgraph IP["`input port assignment (6)`"]
        IPORT["`**input port**
        _includes:_
        - channel`"]
    end
    subgraph IDEF[input device-level presets/triggers]
        direction TB
        IDEV-->|1 to many|ITRIG["`**input trigger**
        _includes:_
        - note
        - pedal cc`"]
        IDEV["`**input device**`"]-->|1 to many|IPRES
        ITRIG-->|up to 6 to 1|IPRES["`**input preset**
        _includes:_
        - pedal cc minimum value
        - pedal cc maximum value`"]
    end
    subgraph PR["`mapping program (many)`"]
        PROG["`**program**
        _includes:_
        - program change
        - bank select`"]
    end
    subgraph ODEF[output device-level presets/triggers]
        direction TB
        OPRES-->|many to 1|ODEV["`**output device**
        _includes:_
        - channel
        - 0 velocity as note off toggle
        - running status toggle`"]
        OPRES["`**output preset**
        _includes:_
        - note`"]-->|1 to up to 5|OTRIG["`**output trigger**
        _includes:_
        - channel
        - note
        - note off send toggle
        - velocity threshold
        - velocity curve
        - minimum velocity
        - maximum velocity`"]-->|many to 1|ODEV
    end
    subgraph OP["`output port assignment (6)`"]
        OPORT["`**output port**`"]
    end
    SEL(["`**select**`"])-->|1 of up to 255|PR
    IMIDI(["`**MIDI in**`"])-->IPORT-->|1 to 1|IDEV
    IDEF-->|many to 1|PROG
    PROG-->|1 to up to 6|ODEF
    ODEV-->|1 to 1|OPORT-->OMIDI(["`**MIDI out**`"])
```
* Flexible layered approach to mapping:
  * Define input and output devices and trigger definitions – a trigger is always associated to a specific device
  * Assign input and output triggers to presets – one preset can be linked to multiple triggers and the same trigger can be linked to multiple presets (mixing different devices)
  * Assign multiple input and output presets to each other in programs to quickly switch between different configurations
  * Limits:[^1] 255 programs, 4,096 devices, 4,096 presets – there’s no hard limit to the number of triggers
* Send program change and/or bank select commands on program change
* Set trigger dependency to cc value (for example to distinguish between open and closed hi-hat from a 2Box drum module)
* Supports both one note per sound on the same channel and one sound per channel, or a combinations of both – including tonal mapping
* Adjust velocity dynamics (threshold, curve, minimum velocity, maximum velocity)
[^1]: The available memory also limits the number of programs, devices presets and triggers
> [!NOTE]
> **<ins>Cybo-Drummer Mapping Terminology</ins>**\
> ***Input device:*** A drumkit, drumpad, keyboard or other device that outputs MIDI data\
> ***Input trigger:*** The MIDI note that is been sent by an input device when playing a drumpad, key, etc.\
> ***Input preset:*** A combination of input triggers and optional foot pedal settings that can be assigned to trigger an output preset\
> ***Output device:*** A drum computer, sampler, synthesizer or other device that responds to MIDI data\
> ***Output trigger:*** The MIDI channel and/or note that triggers a sound in the output device\
> ***Output preset:*** A combination of output triggers and optional note that can be assigned to be triggered by an input preset\
> ***Program:*** A mapping of one or more input presets to one or more output presets plus optionally program change and/or bank select commands to be sent to output devices
#### Other Features
* MIDI learn: Set one of the input ports to receive midi learn data (note values, channel values, cc numbers, etc.)
* MIDI thru: Set all data[^2] received on one of the input ports to be sent unaltered to one of the output ports 
* MIDI monitor with three views: Show mapping flow (input preset > output preset), MIDI data coming in and MIDI data sent out
[^2]: Except SysEx
## How to Build One?
## How to Use It?
### Overview
<img src="/images/hardware_overview.svg" align="right">

Cybo-Drummer has six MIDI input ports at the front and six MIDI output ports at the back. It has a micro USB port on the left side currently only used for power supply and for updating the firmware.

The user interface displayed on the 2.2 inch TFT screen is organized as follows:
* **Page tabs:** The right edge of the screen shows which of the five pages is selected
* **Title bar:** The top edge of screen shows a title bar, consisting of three elements:
  * On the left the active program is always visible
  * Centrally the title of the active sub-page is shown
  * On the right the number of the active sub-page and how many sub-pages the active page has
* **Sub-page:** The remainder of the screen is taken by the sub-page itself
  * **Blocks:** all sub-pages except those on the monitor page are structured in locks which can be selected to enter input; the active block is highlighted using a dark and light sea green colour

To control Cybo-Drummer’s user interface it has two buttons and two rotary encoders, which usually behave as follows:
* **PAGE/YES:** Keep pressed to select page or sub-page
* **TRIGGER/NO:**
  * *Short press:* Trigger last selected output trigger preset (for testing purposes)
  * *Keep pressed:* Show pop-up to select trigger preset
* **NAV/↕ | DEL:**
  * *Turn:* Navigate / select active block
  * *Press (when a program, device, preset or trigger name block is selected):* Delete program, device, preset or trigger (a confirmation pop-up will show)
* **VAL/↔ | SEL/OPT:**
  * *Turn:* Change value of active block or pop-up
  * *Press:*
    * *When a program, device, preset or trigger name block is selected:* Rename or show options menu
    * *When a button block is selected:* Press/execute button
### Pages and sub-pages
Cybo-Drummer’s user interface is organized in five pages:
* **PRG (Program):** Select and edit routing programs
* **IN (Input):** Edit input port assignments, input device setting, input trigger settings and input preset settings
* **OUT (Output):** Edit output port assignments, output device setting, output trigger settings and output preset settings
* **MON (Monitor):** Show router and MIDI monitors
* **SET (Settings):** Adjust global settings

<img src="/images/hardware_pages.svg" align="right">

To change the pages and sub-pages, keep the PAGE button pressed and turn the VAL/↔ knob (right knob) to change the page and the NAV/↕ know (left knob) to change the sub-page. While the PAGE button is pressed the page tabs and title bar are highlighted in dark and light sea green.
### Trigger presets
<img src="/images/hardware_trigger.svg" align="right">

Short pressing the TRIGGER button triggers the last selected output trigger preset (for testing purposes). Long pres the TRIGGER button to show a trigger preset selection pop-up. Keep the TRIGGER button pressend and turn the VAL/↔ knob to change the selected output trigger preset.
### Confirmation Pop-Ups
<img src="/images/hardware_confirmation.svg" align="right">

Cybo-Drummer doesn’t have an undo feature, so to avoid accidentially losing data confirmation pop-ups will show up before deleting something, changing an unsaved program, restoring a back-up or doing a factory reset. Answer the question in the pop-up by pressing the left button for YES and the right button for NO.
### Description of All Pages and Sub-Pages
#### PRG (Program)
The program page is the first page that shows when powering up Cybo-Drummer. Use this page to select or edit the active program.
##### PRG 1/3 – Program: Mapping
<img src="/screenshots/prg_1.png" align="right">

###### program
###### input device
###### input preset
###### output device 1 to 4
###### output preset 1 to 4
> [!IMPORTANT]
> Output device 1 to 4 and output preset 1 to 4 are the output mapping for the above selected input preset. So, to map an input preset to an output preset, first select the input device and input preset, then assign the output devices and output presets. This is indicated by the orange bar between input device/preset and output devices/presets.
##### PRG 2/3 – Program: Program Change
<img src="/screenshots/prg_2.png" align="right">

###### p1 to p6
##### PRG 3/3 – Program: Bank Select
<img src="/screenshots/prg_3.png" align="right">

###### p1 to p6
#### IN (Input)
Use the input page to review or edit input port assignments, input device setting, input trigger settings and input preset settings
##### IN 1/3 – Input Ports
<img src="/screenshots/in_1.png" align="right">

###### p1 to p6 device
###### p1 to p6 channel
##### IN 2/3 – Input Devices/Triggers
<img src="/screenshots/in_2.png" align="right">

###### input device
###### input trigger
###### note
###### pedal cc
> [!IMPORTANT]
> Note and pedal cc relate to the above selected input trigger. This is indicated by the orange bar between input device/trigger and note.
##### IN 3/3 – Input Presets
<img src="/screenshots/in_3.png" align="right">

###### input device
###### input trigger
###### pedal cc min
###### pedal cc max
###### trigger 1 to 6
> [!IMPORTANT]
> Pedal CC min/max and input trigger 1 to 6 are the input trigger mapping for the above selected input preset. So, to map a trigger to a preset, first select the input device and input preset, then assign the CC range and triggers. This is indicated by the orange bar between input device/preset and pedal CC min/max.
#### OUT (Output)
Use the output page to review or edit output port assignments, output device setting, output trigger settings and output preset settings
> [!TIP]
> Output channel can be set at device level (OUT 2/4) or at trigger level (OUT 3/4). Set the device-level channel setting if all a device’s triggers use the same channel (typically assigned to different notes on the same channel). Set the trigger-level channel setting if each trigger uses a different midi channel. If neither device-level, nor trigger-level channel is set, triggers are sent to channel 10.
> [!TIP]
> Output note values can be set at trigger level (OUT 3/4) and at preset level (OUT 4/4). The trigger-level setting is the default for each preset which maps to that trigger, while if a preset-level note is set, that overrules the note setting for that particular preset. This can be used to play tonally (for those drum computers or other MIDI instruments which support that), for example by assigning the same trigger to multiple toms on the input device, but set different notes to tune them differently. If neither trigger-level nor preset-level note is set, note number 60 (C4, middle C) is used.
##### OUT 1/4 – Output Ports
<img src="/screenshots/out_1.png" align="right">

###### p1 to p6 device 
##### OUT 2/4 – Output Devices
<img src="/screenshots/out_2.png" align="right">

###### output device
###### channel
###### 0 velocity as note off
###### running status
> [!IMPORTANT]
> Channel and note off settings and running status settings relate to the above selected output device. This is indicated by the orange bar between output device and channel.
##### OUT 3/4 – Output Triggers
<img src="/screenshots/out_3.png" align="right">

###### ouptut device
###### channel
###### note
###### send note off
###### vel threshold
<img src="/images/velocity_curves_threshold.svg" align="right">

###### velocity curve
<img src="/images/velocity_curves.svg" align="right">

###### min velocity / max velocity
<img src="/images/velocity_curves_scaling.svg" align="right">

> [!IMPORTANT]
> Channel, note, note off settings and velocity dynamics settings cc relate to the above selected output trigger. This is indicated by the orange bar between output device/trigger and channel.
##### OUT 4/4 – Output Presets
<img src="/screenshots/out_4.png" align="right">

###### output device
###### output preset
###### trigger 1 to 6
###### note (1 to 6)
> [!IMPORTANT]
> Onput trigger 1 to 6 and note (1 to 6) are the output trigger mapping for the above selected output preset. So, to map a trigger to a preset, first select the output device and output preset, then assign the triggers. This is indicated by the orange bar between output device/preset and trigger 1 / note.
#### MON (Monitor)
Use the monitor page to monitor the router, MIDI data coming in or MIDI data going out.
##### MON 1/3 – Monitor Routing
<img src="/screenshots/mon_1.png" align="right">

##### MON 2/3 – Monitor MIDI In
<img src="/screenshots/mon_2.png" align="right">

##### MON 3/3 – Monitor MIDI Out
<img src="/screenshots/mon_3.png" align="right">

#### SET (Settings)
Use the settings page to adjust global settings, to backup or recover data or to find the firmware version number.
##### SET 1/2 – Settings: MIDI Thru
<img src="/screenshots/set_1.png" align="right">

##### SET 2/2 – Settings: Other
<img src="/screenshots/set_2.png" align="right">

![screenshot of delete pop-up](/screenshots/prg_1_delete.png)
![screenshot of menu pop-up](/screenshots/prg_1_menu.png)
![screenshot of rename pop-up](/screenshots/prg_1_rename.png)
![screenshot of move pop-up](/screenshots/prg_1_move.png)
![screenshot of trigger pop-up](/screenshots/prg_1_trigger.png)
![screenshot of pages pop-up](/screenshots/prg_1_pages.png)
![screenshot of program changed](/screenshots/prg_1_changed.png)
![screenshot of save changes confirmation pop-up](/screenshots/prg_1_save.png)
![screenshot of not saved confirmation pop-up](/screenshots/set_2_unsaved.png)

![screenshot of store back-up confirmation pop-up](/screenshots/set_2_back-up.png)
![screenshot of restore back-up confirmation pop-up](/screenshots/set_2_restore.png)
![screenshot of factory reset confirmation pop-up](/screenshots/set_2_factory_reset.png)
## Why in Micropython?
A MIDI router/mapper is a time-sensitive application, so why not using the programming language which leads to the fastest possible code (that would be C++ on a Raspberry Pi Pico)? Well… I do am aware that MicroPython is much slower, but I decided to use it anyway, because besides solving my challenge to connect my electronic drum kit to my drum computers, I had a second goal: finally learning how to use Python. You see, I’ve used several programming languages over time (starting with BASIC when I was a child, then Turbo Pascal as a teenager in the 90s, later a bit or C/C++ at university, some JavaScript, a lot of VBA and more recently some Arduino code. But now, for my job, I’m managing analysts who are using Python as their go-to language, so I decided it was time to finally master that language as well. This project was a great learning journey!

I spent a lot of time optimising the code (for speed and memory usage) and it turns out Micropython on a Raspberry Pi Pico is fast enough after all. Keep in mind MIDI is a 40+ year old protocol, so it is pretty slow by today’s standards – enough time between two MIDI bytes to run a bit of Python code.

To keep latency to a minimum the second core is dedicated to MIDI handling, while the primary core takes care of the graphic user interface and button and rotary encoder input. In that way the second core runs a light loop doing only time-sensitive MIDI routing, while the primary core does all the heavy stuff.
## Known Issues
* Add program doesn’t check if maximun number of programs (255) is reached
## Ideas for Features to be Added
* Add MIDI clock distribution
* Add MIDI CC mapping (doing crazy things with the hihat foot pedal)
* Add USB MIDI input/output
* Add filter options to MIDI monitor
## Licencing
The fonts used for the logo and the (future) front panel are Soviet Regular and Soviet X-Expanded, (c) 2003 Dan Zadorozny – [Iconian Fonts](https://www.iconian.com), published with the following copyright statement:
> This font may be freely distributed and is free for all non-commercial uses.  This font is e-mailware; that is, if you like it, please e-mail the author at:
>
> iconian@aol.com

The font used in the graphic user interface is 6x10, from the X11 Linux Window System, copyright [X.Org Fundation](https://x.org), published with the following copyright statement:
> Public domain terminal emulator font. Share and enjoy.
