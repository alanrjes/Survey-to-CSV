import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import json
from pathlib import Path
from utility import change_window

class ManageTemplates(Frame):
    def __init__(self, root):
        self.root=root
        super().__init__(root)
        Button(self, text="Back to Menu", width=25, command=lambda: change_window(self, root.mmFrame)).grid(row=0, column=0)
        Label(self, text="Survey Templates").grid(row=1, column=0, columnspan=2)
        Button(self, text="Open", width=25, command=self.open_template).grid(row=2, column=0)
        Button(self, text="Delete", width=25, command=self.delete_template).grid(row=2, column=1)

        self.selected = ""
        def set_selected(filepath):
            self.selected = filepath

        templates = os.listdir("./templates")
        for i in range(len(templates)):
            f = templates[i]
            Label(self, text=Path(f).stem).grid(row=3+i, column=0, columnspan=2)
            Button(self, text="select", command=lambda: set_selected(f)).grid(row=3+i, column=3)
    
    def open_template(self):
        f = open("./templates/"+self.selected)
        data = json.load(f)
        change_window(self, self.root.csFrame)
        self.root.csFrame.load_template(data)
    
    def delete_template(self):
        pass
