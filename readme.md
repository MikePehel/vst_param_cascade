# VST Param Cascade

A Python tool for automated VST plugin parameter control and batch audio sample generation through MIDI CC automation.

## Features

- Load and control VST3 and Audio Unit plugins
- Create custom MIDI CC parameter mappings
- Generate audio samples across specified note ranges
- Visual parameter configuration through native VST editors
- Configurable sample rate and note duration settings
- Automated file naming based on note, CC number, and parameter values
- Cross-platform compatibility (Windows, macOS, Linux)

## Requirements

- Python 3.x
- VST3 or Audio Unit plugins
- Required Python packages:
  - pedalboard
  - mido
  - numpy
  - tkinter (usually comes with Python)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vst-parameter-cascade.git
cd vst-parameter-cascade
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. From the GUI:
   - Select your VST/AU plugin using the "Browse" button
   - Configure sample rate (44.1kHz - 192kHz)
   - Set note duration (in seconds)
   - Define MIDI note range (default: 42-78)
   - Add MIDI CC mappings with custom labels
   - Set CC values for automation

3. Configure VST:
   - Click "Configure VST" to open the plugin's native editor
   - Set up your initial plugin state
   - Click "Done" when finished

4. Run Automation:
   - Click "Run Automation" to start the process
   - Audio files will be saved in the `output` directory

## Output Files

Generated audio files follow this naming convention:
```
{note_name}_cc{cc_number}_{cc_label}_{cc_value}.wav
```
Example: `C4_cc1_Cutoff_64.wav`

## Project Structure

- `main.py` - Main application and GUI implementation
- `gui_components.py` - Custom Tkinter components for CC mapping and values
- `vst_automation.py` - Core VST automation and audio processing logic

## Default Plugin Directories

The application looks for plugins in these default locations:

- Windows: `C:/Program Files/Common Files/VST3`
- macOS: `/Library/Audio/Plug-Ins/VST3`
- Linux: `/usr/lib/vst3`

## Error Handling

The application includes comprehensive error handling and logging:
- Logs are written with timestamps and debug information
- GUI displays user-friendly error messages
- Validation for all user inputs


## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

## Credits

- Uses [Pedalboard](https://github.com/spotify/pedalboard) for VST hosting
- MIDI handling through [Mido](https://github.com/mido/mido)
- Built with Python's Tkinter GUI framework