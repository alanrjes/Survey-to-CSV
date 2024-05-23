from tkinter import *
from tkinter import messagebox
from create import CreateSurvey
from scan import ScanSurvey
from manage import ManageTemplates
from utility import change_window

class Application(Tk):
    def __init__(self):
        super().__init__()
        self.minsize(600, 400)
        self.title("Survey to CSV")
    
        # create utility pages
        self.csFrame = CreateSurvey(self)
        self.lsFrame = ManageTemplates(self)
        self.ssFrame = ScanSurvey(self)

        # create main menu page
        self.mmFrame = Frame(self)
        Label(self.mmFrame, text="Main Menu").grid()
        Button(self.mmFrame, text="Create New Survey", width=25, command=lambda: change_window(self.mmFrame, self.csFrame)).grid()
        Button(self.mmFrame, text="Manage Survey Templates", width=25, command=lambda: change_window(self.mmFrame, self.lsFrame)).grid()
        Button(self.mmFrame, text="Scan Surveys", width=25, command=lambda: change_window(self.mmFrame, self.ssFrame)).grid()

        self.mmFrame.grid()
        self.mainloop()

Application()
