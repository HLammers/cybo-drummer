# Cybo-Drummer
**Humenize those drum computers!**

(c) 2024 Harm Lammers
## Introduction
I own an electronic drum kit and a bunch of drum computers and my dream was to use the former to play the latter, so I went searching for a way to do just that - allowing me to easily switch between different configurations combining the sounds of one or more drum computers. I looked for hardware solutions, but couldn't find any. I looked for software solutions, but I could only find MIDI mappers or other complex solutions that would never give me the easy to use experience I had it mind. It turns out that (as usual) I go against the current fashion of trying to make an electronic drum kit sound (and look) as acoustic as possible. So I decided to develop my own solution - and publish it as open source DIY project, hoping it finds like-minded drummers!
## What Is It?
Cybo-Drummer is a MIDI mappers specially designed for mapping drum triggers (electronic drum kits' brains) to drum computers. Since there is no standard for the MIDI messages sent by drum kits, nor the messages received by drum computers, Cybo-Drummer offers a flexible way of mapping the one to the other.

The idea for the hardware was inspired by the work of [diyelectromusic (Kevin)](https://diyelectromusic.com/), in particular his [Raspberry Pi Pico Multi MIDI Router](https://diyelectromusic.com/2022/09/19/raspberry-pi-pico-multi-midi-router-part-5/). The first prototype is an additional pcb on top of the Multi Midi Router.
### Features
* 6 DIN MIDI input ports
* 6 DIN MIDI output ports
## How to Build One?
## How to Use It?
## Why in Micropython?
## Known Issues
## Ideas for Features to be Added
* Velocity mapping (minimum velocity, maximum velocity, velocity curves)
* MIDI clock distribution
* MIDI CC mapping (doing crazy things with the hihat foot pedal)
## Licencing