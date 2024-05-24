import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import pdfkit
import json
from pathlib import Path

class CreateSurvey(Frame):
    def __init__(self, root):
        self.root=root
        super().__init__(root)
        Button(self, text="Back to Menu", width=25, command=self.back_to_menu).grid(row=0, column=0)
        Label(self, text="Create Survey").grid(row=1, columnspan=3)
        Button(self, text="Save Template", width=25, command=self.save_template).grid(row=1, column=0)
        Button(self, text="Print to PDF", width=25, command=self.print_survey).grid(row=1, column=1)

        Label(self, text="Survey title:").grid(row=2, column=0)
        self.title = Entry(self)
        self.title.grid(row=2, column=1)
        Label(self, text="Subtitle:").grid(row=3, column=0)
        self.subtitle = Entry(self)
        self.subtitle.grid(row=3, column=1)
        Label(self, text="Instructions:").grid(row=4, column=0)
        self.instructions = Entry(self)
        self.instructions.grid(row=4, column=1)

        Button(self, text="Add Question", command=self.add_question).grid(row=5, column=0)
        Button(self, text="Delete Question", command=self.delete_question).grid(row=5, column=1)
        self.questions = []

        self.filename = None
        self.replace = False  # for template renaming, delete previous-named file
    
    def add_question(self):
        i = len(self.questions)
        q = Entry(self)
        q.grid(row=i+6, column=0)
        self.questions.append(q)
    
    def delete_question(self):
        if len(self.questions)>0:
            q = self.questions.pop()
            q.destroy()
    
    def back_to_menu(self):
        # clear question fields
        for q in self.questions:
            q.destroy()
        self.questions = []
        self.title.delete(0, 'end')
        self.subtitle.delete(0, 'end')
        self.instructions.delete(0, 'end')
        self.root.change_window(self)
    
    @staticmethod
    def naming_shenanigans(name, directory):
        if name == "":
            name = "Survey"
        i = 1
        usedNames = os.listdir(directory)
        tempName = name
        while tempName+".pdf" in usedNames:
            tempName = name + "("+str(i)+")"
            i+=1
        return tempName

    
    def print_survey(self):
        self.filename = self.naming_shenanigans(self.title.get(), Path("./print"))
        
        # build PDF
        def print_questions():  # helper for printing out questions & bubbles
            scale = ["Strongly Disagree", "Somewhat Disagree", "Neutral", "Somewhat Agree", "Strongly Agree"]
            labels = "".join(["<td style='padding: 5px; text-align: center; border-bottom: 1px solid black'>"+s+"</td>" for s in scale]) + "<td style='border-bottom: 1px solid black'>"
            bubbles = "<td style='padding: 5px; text-align: center; font-size: 12pt'>&#x25EF</td>"*5 + "<td style='padding: 5px; font-size: 12pt'>&#x25C2</td>"

            htmlstr = "<tr><td style='padding-left: 10px; border-right: 1px solid black; border-bottom: 1px solid black'><b>Questions</b></td>"+labels

            i = 1
            for q in self.questions:
                htmlstr += '''<tr style="border-top: 1px dashed silver">
                                <td style="padding-right: 10px; padding-top: 10px; padding-bottom: -10px; width: 100%; border-right: 1px solid black">
                                    <ol style="padding-left: 50px"><li value="'''+str(i)+'">'+q.get()+'''</li></ol>
                                </td>
                                '''+bubbles+'''
                            </tr>'''
                i+=1
            htmlstr += "<tr style='border-right: 1px solid black; border-left: 1px solid black; border-bottom: 1px solid black'><td style='border-right: 1px solid black'></td>"+"<td style='text-align: center'>&#x25B4</td>"*5+"<td></td></tr>"
            
            return "<table style='width: 100%; border-collapse: collapse; border: 1px solid black'>"+htmlstr+"</table>"

        HTMLstring = '''
            <h1>'''+self.title.get()+'''</h1>
            <h2>'''+self.subtitle.get()+'''</h2>
            <body>
                <p>'''+self.instructions.get()+'''</p>
                '''+print_questions()+'''
            </body>
        '''

        # save to PDF
        pdfkit.from_string(HTMLstring, Path("./print/"+self.filename+".pdf"),
            options = { 'page-size': 'Letter',
                        'margin-top': '0.6in',
                        'margin-right': '0.6in',
                        'margin-bottom': '0.6in',
                        'margin-left': '0.6in'},
        )

        messagebox.showinfo("Saved", "Printed to PDF")

    def save_template(self):
        if self.replace:  # case of editing template; erase previous version
            os.remove(Path("./templates/"+self.filename))
        
        self.filename = self.naming_shenanigans(self.title.get(), Path("./templates"))

        templateDict = {"title": self.title.get(),
                        "subtitle": self.subtitle.get(),
                        "instructions": self.instructions.get(),
                        "questions": [q.get() for q in self.questions]}

        # save to JSON
        with open(Path("./templates/"+self.filename+".json"), "w+") as f:
            json.dump(templateDict, f)

        messagebox.showinfo("Saved", "Saved as template")
    
    def load_template(self, filename, preset, replace):  # replace parameter is True if editing and False if duplicating
        self.replace = replace
        self.filename = filename
        self.title.insert(END, preset["title"])
        self.subtitle.insert(END, preset["subtitle"])
        self.instructions.insert(END, preset["instructions"])
        for q in preset["questions"]:
            self.add_question()
            self.questions[-1].insert(END, q)
