import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import json
from pathlib import Path

class ManageTemplates(Frame):
    def __init__(self, root):
        self.root=root
        super().__init__(root)
        Button(self, text="Back to Menu", width=25, command=lambda: self.root.change_window(self)).grid(row=0, column=0)
        Label(self, text="Survey Templates").grid(row=1, column=0, columnspan=3)
        Button(self, text="Edit", width=25, command=self.open_template).grid(row=2, column=0)
        Button(self, text="Duplicate", width=25, command=self.duplicate_template).grid(row=2, column=1)
        Button(self, text="Delete", width=25, command=self.delete_template).grid(row=2, column=2)

        self.selected = ""
        self.fileList = Frame(self)
        self.fileList.grid()
    
    def set_selected(self, filepath):
        self.selected = filepath

    def list_templates(self):
        templates = os.listdir(Path("./templates"))
        for i in range(len(templates)):
            f = templates[i]
            Label(self.fileList, text=Path(f).stem).grid(row=3+i, column=0, columnspan=2)
            Button(self.fileList, text="select", command=lambda: self.set_selected(f)).grid(row=3+i, column=2, sticky=E)
    
    def open_template(self):
        with open(Path("./templates/"+self.selected), "r") as f:
            data = json.load(f)
            self.root.change_window(self, self.root.csFrame)
            self.root.csFrame.load_template(self.selected, data, True)
    
    def duplicate_template(self):
        with open(Path("./templates/"+self.selected), "r") as f:
            data = json.load(f)
            self.root.change_window(self, self.root.csFrame)
            self.root.csFrame.load_template(self.selected, data, False)
    
    def delete_template(self):
        if messagebox.askquestion("Delete template", "Are you sure you want to delete this template?") == "yes":
            os.remove(Path("./templates/"+self.selected))
            for widget in self.fileList.winfo_children():  # destroy all and reload w/out deleted file to remove gaps
                widget.destroy()
            self.list_templates()
