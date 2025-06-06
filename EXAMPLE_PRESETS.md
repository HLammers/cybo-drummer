<header>
<img src="logos/colour_logo.svg" width="100%">

# Cybo-Drummer

**Humanize those drum computers!**

&copy; 2024&ndash;2025 Harm Lammers
</header>
<main>

# Example Presets

This file is part of a series of documentation files on Cybo-Drummer:

* [README file](README.md) with brief introduction
* [User Manual](USER_MANUAL.md)
* [Building Instructions](BUILDING_INSTRUCTIONS.md)
* Example Presets (this file)
* [Development Roadmap](TO_DO.md)

## Introduction

Since Cybo-Drummer doesn&rsquo;t make any sound on its own, but merely routes signals from one device to another, it isn&rsquo;t possible to make meaningful factory presets. The presets shared in the [example presets folder](example_presets/) are based on my personal setup, but can be useful as examples. Currently they reflect a baseline for equipment I own, but that will probably evolve over time. I haven&rsquo;t updated them yet, for example, to make use of the old Roland SPD-11 I bought a while ago, and they do not make use yet of the most recently added features.

<!--update version number in the two references to MicroPython below when necessary!-->

> [!TIP]
> To upload the example presets to Cybo-Drummer, follow the same instructions as given for restoring a back-up when [uploading firmware](README.md#uploading-firmware):
>
> * If you haven&rsquo;t before: Install [Python](https://www.python.org/downloads) &ndash; follow the instructions provided [here](https://docs.python.org/3/using/windows.html#windows-full) and **make sure to select &lsquo;Add Python 3.x to PATH&rsquo;**
> * If you haven&rsquo;t before: Download the source code of [MicroPython release v1.25.0](https://github.com/micropython/micropython/releases). (typically the zip version) and unzip it somewhere on your PC
> * In File Explorer go to the micropython-1.25.0\tools\mpremote folder (in the location where you unzipped MicroPython)
> * Right click somewhere in the folder (not on a file) and from the context menu select &lsquo;Open in Terminal&rsquo;
> * If you do it for the first time: type the following to install required Python modules:
>
>   ```
>   pip install pyserial
>   pip instal importlib_metadata
>   ```
>
> * Copy the data_files folder from the [example presets folder](example_presets/) to the micropython-1.24.0\tools\mpremote folder
> * On your PC type `py mpremote.py fs cp -r data_files/ :` **without pressing ENTER** (so not executing it yet)
> * While you keep Cybo-Drummer&rsquo;s TRIGGER button pressed:
>   * Press RESET button on Cybo-Drummer
>   * Press ENTER on your PC to start downloading (backing up) or uploading (restoring)

Below I share some details on the different devices in the example presets, including what I learned so far about setting them up for Cybo-Drummer.

## Input Device: 2Box

My drum kit is a Fame Hybrid Pro, which is produced by 2Box and which is in fact a derivative of 2Box&rsquo;s DrumIt series (it uses the same firmware). The default 2Box input triggers are based on 2Box&rsquo;s default MIDI mapping, with one addition specific to the Fame module: 2Box calls numbers the three cymbals 1, 2 and 3, but which of those are the ride, 1<sup>st</sup> crash and 2<sup>nd</sup> crash seems to be different depending on which type of module.

> [!NOTE]
> By default 2Box modules use MIDI CC 4 to send the position of the hi-hat foot pedal (default setting: 0 = fully open, 127 = fully closed). The hi-hat sends the same MIDI note when open or closed, so the CC 4 value needs to be checked to distinguish between both.

## Output Device: Drumbrute

This device is set up for the factory settings of the Arturia Drumbrute, but since the Drumbrute can&rsquo;t store presets, that only means the default MIDI channel and default note mapping.

> [!NOTE]
> The Arturia Drumbrute doesn&rsquo;t respond to MIDI program change nor bank select messages.

## Output Device: Drumlogue

This device is set up for the factory settings of the Korg Drumlogue, with only one adjustment: the MIDI mode is set to multi-channel 7-2 (on the Drumlogue: SHIFT + GLOBAL &rarr; 7 &rarr; set CH to 7-2), so the Multi Engine can be played tonally. There are 64 Drumlogue presets, linked to the Drumlogue&rsquo;s 64 factory kits.

> [!NOTE]
> The Korg Drumlogue does not respond to MIDI bank select messages, only to program change, but with a twist: MIDI program change value 2 (counting from 1) is kit A1, 3 is kit A2, 18 is B1, etc.

> [!IMPORTANT]
> Make shure to update the Korg Drumlogue to the latest version of the firmware, because version 1.2.0 had a bug which is fixed in version 1.3.0: it didn&rsquo;t respond to MIDI program change values 16, 32, 48, 64, etc. (counting from 0).

## Output Device: LXR-02

This device is set up for the first factory project of the Sonic Portions × Erica Synths LXR-02 (HrtlKits). It assumes the global MIDI channel to be set to the default 1, which the LXR-02 calls 0 (on the LXR-02: SHIFT + CONFIG &rarr; set CH to 0) and the LXR-02 is set to receive program change, control change and note messages (on the LXR-02: SHIFT + CONFIG &rarr; turn DATA knob to scroll to second page &rarr; set MRX to &lsquo;all&rsquo; or &lsquo;PCN&rsquo;).

> [!NOTE]
> The Sonic Portions × Erica Synths LXR-02 responds both to program change and bank select messages: program change messages change patterns, bank select messages (not mentioned in the user manual: MSB only) change kits. Kits are saved per project and it isn&rsquo;t possible to change the project via MIDI.
>
> The LXR-02&rsquo;s manual description of the MIDI implementation and what is saved where (kits, patterns, projects) is rather incomplete. It doesn&rsquo;t indicate, for example, where output routing and FX settings are stored. Searching the internet provides some hints based on other people&rsquo;s experience it&rsquo;s stored with kits, but I haven&rsquo;t yet tested it myself.  

> [!CAUTION]
> Make sure not to assign one of the LXR-02&rsquo;s voices to same MIDI channel which is assigned to the LXR-02&rsquo;s global channel, because triggering that channel will trigger the selected voice on the LXR-02.

> [!TIP]
> Best is to prepare a special project to use LXR-02 effectively with Cybo-Drummer:
>
> * Initiate a new project: press LOAD + PROJECT &rarr; select an EMPTY project &rarr; press DATA knob
> * Set kit change mode to &lsquo;off&rsquo; to separate kits from patterns: press SHIFT + CONFIG &rarr; turn DATA knob to scroll to third page &rarr; set KCM to &lsquo;off&rsquo;
> * In pattern 1 (the default pattern after initiating a new project), assign voices to MIDI channels 2 to 8 (channel 0 is used as global channel, so triggering that channel will trigger the selected voice on the LXR-02) and set each voice to respond any note (allowing to tune it from Cybo-Drummer or to play it tonally):
>   * Press VOICE &rarr; press MIX &rarr; turn DATA knob to scroll to second page
>   * Press DRUM1 button (below sliders) &rarr; set CH to 2 and set NTE to &lsquo;any&rsquo;
>   * Press DRUM2 button (below sliders) &rarr; set CH to 3 and set NTE to &lsquo;any&rsquo;
>   * Press DRUM3 button (below sliders) &rarr; set CH to 4 and set NTE to &lsquo;any&rsquo;
>   * Press SNARE button (below sliders) &rarr; set CH to 5 and set NTE to &lsquo;any&rsquo;
>   * Press CLP/CYM button (below sliders) &rarr; set CH to 6 and set NTE to &lsquo;any&rsquo;
>   * Press CL HH button (below sliders) &rarr; set CH to 7 and set NTE to &lsquo;any&rsquo;
>   * Press OP HH button (below sliders) &rarr; set CH to 8 and set NTE to &lsquo;any&rsquo;
> * Save project:
>   * Press SAVE + PROJECT &rarr; press DATA knob
>   * Turn DATA knob to select &lsquo;Y&rsquo; &rarr; press DATA knob
>   * Change name: Turn DATA knob to select character to change &rarr; press DATA knob &rarr; turn DATA knob to select character &rarr; press DATA knob to confirm; &rarr; finish editing by selecting &lsquo;ok&rsquo; (turn DATA knob clockwise until it is selected) and pressing DATA knob
> * Turn off the LXR-02, take out the SD card and use a PC to copy the kits (files with .SND extension) you&rsquo;d like to use into the newly created project folder (called PROJ##, where # is the project number) and rename them so they start with &lsquo;01-&rsquo; to &lsquo;63-&rsquo;
> * Put the SD card back into the LXR-02 and load the project: press LOAD + PROJECT &rarr; select the project &rarr; press DATA knob

## Output Device: Volca Drum

This device is set up for a Korg Volca Drum in default split channel mode (in which parts 1 to 6 are assigned to MIDI channels 1 to 6 respectively). There are 16 Volca Drum programs, linked to program 1 to 16 of the Volca Drum.

> [!NOTE]
> The Volca drum does not respond to MIDI bank select messages, only to program change. Program changes messages 1 to 16 (counting from 1) select Volca Drum programs 1 to 16, each of which has a sequence and a kit assigned, so to make best use of the Volca Drum with Cybo-Drummer, assign each kit to a separate program.

</main>