<header>
<img src="logos/colour_logo.svg" width="100%">

# Cybo-Drummer

**Humanize those drum computers!**

&copy; 2024&ndash;2025 Harm Lammers
</header>
<main>

# Development Roadmap

This file is part of a series of documentation files on Cybo-Drummer:

* [README file](README.md) with brief introduction
* [User Manual](USER_MANUAL.md)
* [Building Instructions](BUILDING_INSTRUCTIONS.md)
* [Example Presets](EXAMPLE_PRESETS.md)
* Development Roadmap (this file)

## Release 0.3.0

- [ ] Test add new voice, rename voice and move voice
- [ ] Prepare schematics files

## Release 0.3.1

*More items from the backlog could get added to the 0.3.1 list if I find the time (or urge), inspiration and right solutions*

- [ ] Double check, test and document reception of bank select / program change messages
- [ ] Double check, test and document MIDI learn
- [ ] Test batch assign multipad notes velocity layer filter

## Backlog for Future Releases

*Some of the things listed here are more likely than others to ever be implemented &ndash; I&rsquo;m happy to hear your ideas for additional features to be considered!*

### MIDI Handling

- [ ] Adding USB MIDI
- [ ] Distribute MIDI System Real Time Messages (Timing Clock, Start, Continue, Stop)

### MIDI Monitor Improvement

- [ ] Adding MIDI monitor filter options
- [ ] Trying to improve monitor screen refresh rate by using a separate FrameBuffer for the monitor sub-page, FrameBuffer.scroll when adding a new line and FrameBuffer.blit to merge it with the main FrameBuffer

### MIDI Mapping

- [ ] Adding MIDI CC mapping (doing crazy things, for example with the hihat foot pedal or an express pedal)
- [ ] Rethinking how to deal with choke events, which for some drum modules lead to MIDI note events (2Box, Alesis?) and for others to poly aftertouch/pressure MIDI CC messages (Roland, Yamaha)
- [ ] Adding choke groups which could combine different devices

### User Interface

- [ ] Change active block on other sub-pages where relevant

### PC Editor

- [ ] Building an editor for program definitions, device/trigger/voices definitions and settings on a PC

### Hardware

- [ ] Building a version of Cybo-Drummer with 3 MIDI in ports and 9 MIDI out ports as an alternative for if needed more outputs

</main>