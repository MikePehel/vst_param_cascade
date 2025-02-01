import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import os
from typing import Optional

from gui_components import CCMappingFrame, CCValuesFrame
from vst_automation import (
    VSTAutomation, 
    AutomationConfig, 
    get_default_plugin_directory,
    find_vst_binary_in_bundle
)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class VSTAutomationGUI(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.title("VST MIDI CC Automation Tool")
        self.geometry("800x600")
        
        self.vst_automation: Optional[VSTAutomation] = None
        self.setup_ui()
        
    def setup_ui(self):
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.setup_vst_selection(main_container)
        
        self.setup_common_settings(main_container)
        
        self.setup_midi_cc_components(main_container)
        
        self.setup_action_buttons(main_container)
        
    def setup_vst_selection(self, parent):
        path_frame = ttk.LabelFrame(parent, text="VST Selection")
        path_frame.pack(fill='x', pady=5)
        
        self.vst_path = tk.StringVar()
        path_entry = ttk.Entry(path_frame, textvariable=self.vst_path)
        path_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_vst)
        browse_btn.pack(side='left', padx=5, pady=5)
        
    def setup_common_settings(self, parent):
        rate_frame = ttk.LabelFrame(parent, text="Sample Rate")
        rate_frame.pack(fill='x', pady=5)
        
        self.sample_rate = tk.StringVar(value="44100")
        rates = ["44100", "48000", "88200", "96000", "192000"]
        for rate in rates:
            ttk.Radiobutton(rate_frame, text=f"{rate} Hz", 
                          variable=self.sample_rate, value=rate).pack(side='left', padx=5)
        
        duration_frame = ttk.LabelFrame(parent, text="Duration (seconds)")
        duration_frame.pack(fill='x', pady=5)
        
        self.duration = tk.StringVar(value="0.5")
        ttk.Entry(duration_frame, textvariable=self.duration, width=10).pack(padx=5, pady=5)
        
        range_frame = ttk.LabelFrame(parent, text="MIDI Note Range")
        range_frame.pack(fill='x', pady=5)
        
        note_frame = ttk.Frame(range_frame)
        note_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(note_frame, text="From:").pack(side='left', padx=2)
        self.note_min = tk.StringVar(value="42")
        ttk.Entry(note_frame, textvariable=self.note_min, width=5).pack(side='left', padx=2)
        
        ttk.Label(note_frame, text="To:").pack(side='left', padx=2)
        self.note_max = tk.StringVar(value="78")
        ttk.Entry(note_frame, textvariable=self.note_max, width=5).pack(side='left', padx=2)
        
    def setup_midi_cc_components(self, parent):
        self.cc_frame = CCMappingFrame(parent)
        self.cc_frame.pack(fill='x', pady=5)
        
        self.values_frame = CCValuesFrame(parent)
        self.values_frame.pack(fill='x', pady=5)
        
        self.values_frame.add_value("0")
        self.values_frame.add_value("100")
        
    def setup_action_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        self.configure_btn = ttk.Button(btn_frame, text="Configure VST", 
                                      command=self.configure_vst, state='disabled')
        self.configure_btn.pack(side='left', padx=5)
        
        self.run_btn = ttk.Button(btn_frame, text="Run Automation", 
                                command=self.run_automation, state='disabled')
        self.run_btn.pack(side='left', padx=5)
            
    def browse_vst(self):
            initial_dir = get_default_plugin_directory()
            os.makedirs(initial_dir, exist_ok=True)
                
            filepath = filedialog.askopenfilename(
                initialdir=initial_dir,
                filetypes=[
                    ("VST3 Plugins", "*.vst3"),
                    ("VST3 Binaries", "*.so *.dll"),
                    ("Audio Units", "*.component *.au"),
                    ("All Files", "*.*")
                ]
            )
            
            if filepath:
                filepath = os.path.normpath(filepath)
                # Try to find the actual VST binary if a bundle was selected
                binary_path = find_vst_binary_in_bundle(filepath)
                if binary_path:
                    filepath = binary_path
                    logger.info(f"Found VST binary in bundle: {filepath}")
                
                logger.info(f"Selected VST path: {filepath}")
                self.vst_path.set(filepath)
                self.configure_btn.config(state='normal')

    def configure_vst(self):
        try:
            self.vst_automation = VSTAutomation(self.vst_path.get())
            self.vst_automation.load_plugin()
            self.vst_automation.show_editor()
            
            dialog = tk.Toplevel(self)
            dialog.title("VST Configuration")
            dialog.geometry("300x100")
            dialog.transient(self)
            dialog.grab_set()
            
            ttk.Label(dialog, 
                     text="Configure the VST and click Done when finished").pack(pady=10)
            ttk.Button(dialog, 
                      text="Done", 
                      command=lambda: self.finish_config(dialog)).pack()
            
        except Exception as e:
            logger.error(f"Failed to load VST: {str(e)}")
            messagebox.showerror("Error", f"Failed to load VST: {str(e)}")
            
    def finish_config(self, dialog):
        dialog.destroy()
        self.run_btn.config(state='normal')
        
    def run_automation(self):
        try:
            if not self.vst_automation:
                messagebox.showerror("Error", "Please configure VST first")
                return
            
            config = AutomationConfig(
                sample_rate=int(self.sample_rate.get()),
                duration=float(self.duration.get()),
                note_min=int(self.note_min.get()),
                note_max=int(self.note_max.get()),
                output_dir="output"
            )
            
            self.vst_automation.run_midi_cc_automation(
                config=config,
                cc_mappings=self.cc_frame.get_mappings(),
                cc_values=self.values_frame.get_values()
            )
                
            messagebox.showinfo(
                "Success", 
                f"Automation completed!\nFiles saved in {config.output_dir}"
            )
                
        except Exception as e:
            logger.error(f"Automation failed: {str(e)}")
            messagebox.showerror("Error", f"Automation failed: {str(e)}")

if __name__ == "__main__":
    app = VSTAutomationGUI()
    app.mainloop()