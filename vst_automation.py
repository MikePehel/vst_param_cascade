import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from pedalboard import Plugin, load_plugin
from pedalboard.io import AudioFile
from mido import Message
import numpy as np

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@dataclass
class AutomationConfig:
    sample_rate: int
    duration: float
    note_min: int
    note_max: int
    output_dir: str = "output"

def midi_to_note_name(midi_number: int) -> str:
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_number // 12) - 1
    note_name = notes[midi_number % 12]
    return f"{note_name}{octave}"

class VSTAutomation:
    
    def __init__(self, plugin_path: str):
        self.plugin_path = plugin_path
        self.plugin: Optional[Plugin] = None
        
    def load_plugin(self) -> None:
        try:
            self.plugin = load_plugin(self.plugin_path)
            logger.info(f"Successfully loaded plugin: {self.plugin_path}")
        except Exception as e:
            logger.error(f"Failed to load plugin: {str(e)}")
            raise
            
    def save_audio(self, audio: np.ndarray, filepath: str, config: AutomationConfig) -> None:
        try:
            with AudioFile(filepath, 'w', config.sample_rate, audio.shape[0]) as f:
                f.write(audio)
            logger.debug(f"Saved audio file: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save audio file {filepath}: {str(e)}")
            raise
            
    def run_midi_cc_automation(self, 
                             config: AutomationConfig,
                             cc_mappings: Dict[int, str],
                             cc_values: List[int]) -> None:
        if not self.plugin:
            raise RuntimeError("Plugin not loaded. Call load_plugin() first.")
            
        os.makedirs(config.output_dir, exist_ok=True)
        
        try:
            for note in range(config.note_min, config.note_max + 1):
                note_name = midi_to_note_name(note)
                for cc_num, cc_label in cc_mappings.items():
                    for cc_val in cc_values:
                        messages = [
                            Message('control_change', control=cc_num, value=cc_val),
                            Message('note_on', note=note, velocity=100),
                            Message('note_off', note=note, velocity=0, time=config.duration)
                        ]
                        
                        audio = self.plugin(messages, 
                                         duration=config.duration,
                                         sample_rate=config.sample_rate)
                        
                        filename = f"{note_name}_cc{cc_num}_{cc_label}_{cc_val}.wav"
                        filepath = os.path.join(config.output_dir, filename)
                        self.save_audio(audio, filepath, config)
                        
            logger.info("MIDI CC automation completed successfully")
            
        except Exception as e:
            logger.error(f"MIDI CC automation failed: {str(e)}")
            raise
            
    def show_editor(self) -> None:
        if not self.plugin:
            raise RuntimeError("Plugin not loaded. Call load_plugin() first.")
        self.plugin.show_editor()

def list_available_plugins(directory: str) -> List[str]:
    extensions = ('.vst3', '.component', '.au')  # Add more if needed
    plugins = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extensions):
                plugins.append(os.path.join(root, file))
                
    return plugins

def get_default_plugin_directory() -> str:
    if os.name == 'nt':  # Windows
        return "C:/Program Files/Common Files/VST3"
    elif os.name == 'posix':  # macOS and Linux
        if os.path.exists("/Library/Audio/Plug-Ins/VST3"):  # macOS
            return "/Library/Audio/Plug-Ins/VST3"
        else:  # Linux
            return "/usr/lib/vst3"
    else:
        return "/"