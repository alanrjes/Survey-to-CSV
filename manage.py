import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from utility import change_window

class ManageTemplates(Frame):
    def __init__(self, root):
        self.root=root
        super().__init__(root)
        Button(self, text="Back to Menu", width=25, command=lambda: change_window(self, root.mmFrame)).grid()
        Label(self, text="Survey Templates").grid()
        # TBD
