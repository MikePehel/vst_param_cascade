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

def find_vst_binary_in_bundle(path: str) -> Optional[str]:
    """
    Find the actual VST binary (.so, .vst3, .dll) within a VST3 bundle directory structure.
    
    Args:
        path: Path to either a VST3 bundle directory or direct binary
        
    Returns:
        str: Path to the actual VST binary, or None if not found
    """
    # If path is already a binary file, return it
    if os.path.isfile(path):
        _, ext = os.path.splitext(path.lower())
        if ext in ['.so', '.vst3', '.dll', '.component', '.au']:
            return path
        return None
        
    # Handle VST3 bundle directory structure
    if path.lower().endswith('.vst3') and os.path.isdir(path):
        # Common VST3 bundle paths by platform
        if os.name == 'nt':  # Windows
            binary_path = os.path.join(path, 'Contents', 'x86_64-win', '*.vst3')
        elif os.name == 'posix':  # Linux and macOS
            if os.path.exists('/Library'):  # macOS
                binary_path = os.path.join(path, 'Contents', 'MacOS', '*.component')
            else:  # Linux
                # Check both x86_64-linux and x86_64 directories
                linux_dirs = ['x86_64-linux', 'x86_64']
                for linux_dir in linux_dirs:
                    base_path = os.path.join(path, 'Contents', linux_dir)
                    if os.path.exists(base_path):
                        # Look for both .so and .vst3 files
                        for ext in ['.so', '.vst3']:
                            plugin_name = os.path.basename(path).replace('.vst3', ext)
                            full_path = os.path.join(base_path, plugin_name)
                            if os.path.exists(full_path):
                                return full_path
                            
                        # If named file not found, look for any .so or .vst3 file
                        for ext in ['.so', '.vst3']:
                            files = [f for f in os.listdir(base_path) if f.endswith(ext)]
                            if files:
                                return os.path.join(base_path, files[0])
                                
        logger.debug(f"No VST binary found in bundle: {path}")
        return None
        
    return None

def get_default_plugin_directory() -> str:
    """Get the default VST plugin directory for the current platform."""
    if os.name == 'nt':  # Windows
        return "C:/Program Files/Common Files/VST3"
    elif os.name == 'posix':  # macOS and Linux
        if os.path.exists("/Library/Audio/Plug-Ins/VST3"):  # macOS
            return "/Library/Audio/Plug-Ins/VST3"
        else:  # Linux
            # Check common Linux VST directories
            linux_vst_dirs = [
                "/usr/lib/vst3",
                "/usr/local/lib/vst3",
                os.path.expanduser("~/.vst3")
            ]
            for dir in linux_vst_dirs:
                if os.path.exists(dir):
                    return dir
            # Return first path as default if none exist
            return linux_vst_dirs[0]
    return "/"

def list_available_plugins(directory: str) -> list[str]:
    plugins = []
    vst_extensions = ('.vst3', '.component', '.au', '.so')
    
    for root, _, files in os.walk(directory):
        # Check files with VST extensions
        for file in files:
            if file.lower().endswith(vst_extensions):
                full_path = os.path.join(root, file)
                # For .vst3 directories, look inside the bundle
                if os.path.isdir(full_path) and full_path.lower().endswith('.vst3'):
                    binary_path = find_vst_binary_in_bundle(full_path)
                    if binary_path:
                        plugins.append(binary_path)
                else:
                    plugins.append(full_path)
                    
    return plugins