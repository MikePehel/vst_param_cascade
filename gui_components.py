import tkinter as tk
from tkinter import ttk
from typing import Dict, List

class CCMappingFrame(ttk.LabelFrame):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, text="MIDI CC Mappings", *args, **kwargs)
        self.cc_mappings: List[Dict] = []
        self.setup_ui()
        
    def setup_ui(self):
        self.add_btn = ttk.Button(self, text="Add CC Mapping", command=self.add_cc_mapping)
        self.add_btn.pack(pady=5)
        
        self.mappings_frame = ttk.Frame(self)
        self.mappings_frame.pack(fill='x', expand=True)
        
    def add_cc_mapping(self):
        mapping_frame = ttk.Frame(self.mappings_frame)
        mapping_frame.pack(fill='x', pady=2)
        
        ttk.Label(mapping_frame, text="CC#:").pack(side='left', padx=2)
        cc_num = ttk.Entry(mapping_frame, width=5)
        cc_num.pack(side='left', padx=2)
        
        ttk.Label(mapping_frame, text="Label:").pack(side='left', padx=2)
        label = ttk.Entry(mapping_frame, width=20)
        label.pack(side='left', padx=2)
        
        remove_btn = ttk.Button(mapping_frame, text="×", width=3,
                              command=lambda: self.remove_mapping(mapping_frame))
        remove_btn.pack(side='right', padx=2)
        
        self.cc_mappings.append({
            'frame': mapping_frame,
            'cc_num': cc_num,
            'label': label
        })
        
    def remove_mapping(self, frame):
        frame.destroy()
        self.cc_mappings = [m for m in self.cc_mappings if m['frame'] != frame]
        
    def get_mappings(self) -> Dict[int, str]:
        return {
            int(m['cc_num'].get()): m['label'].get()
            for m in self.cc_mappings
            if m['cc_num'].get().isdigit()
        }

class CCValuesFrame(ttk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, text="CC Values", *args, **kwargs)
        self.values: List[tk.StringVar] = []
        self.setup_ui()
        
    def setup_ui(self):
        self.add_btn = ttk.Button(self, text="Add Value", command=self.add_value)
        self.add_btn.pack(pady=5)
        
        self.values_frame = ttk.Frame(self)
        self.values_frame.pack(fill='x', expand=True)
        
    def add_value(self, initial_value="0"):
        value_frame = ttk.Frame(self.values_frame)
        value_frame.pack(fill='x', pady=2)
        
        value_var = tk.StringVar(value=initial_value)
        value_entry = ttk.Entry(value_frame, textvariable=value_var, width=5)
        value_entry.pack(side='left', padx=2)
        
        remove_btn = ttk.Button(value_frame, text="×", width=3,
                              command=lambda: self.remove_value(value_frame))
        remove_btn.pack(side='right', padx=2)
        
        self.values.append({
            'frame': value_frame,
            'var': value_var
        })
        
    def remove_value(self, frame):
        frame.destroy()
        self.values = [v for v in self.values if v['frame'] != frame]
        
    def get_values(self) -> List[int]:
        return [int(v['var'].get()) for v in self.values if v['var'].get().isdigit()]