import os
from tkinter import *
import pdfkit

# global utility function:
def change_window(currentFrame, nextFrame):
    currentFrame.grid_forget()
    nextFrame.grid()

class Application(Tk):
    def __init__(self):
        super().__init__()
        self.minsize(600, 400)
        self.title("Survey to CSV")
    
        # create utility pages
        csFrame = CreateSurvey(self)
        lsFrame = ManageTemplates(self)
        ssFrame = ScanSurvey(self)

        # create main menu page
        self.mmFrame = Frame(self)
        Label(self.mmFrame, text="Main Menu").grid()
        Button(self.mmFrame, text="Create New Survey", width=25, command=lambda: change_window(self.mmFrame, csFrame)).grid()
        Button(self.mmFrame, text="Manage Survey Templates", width=25, command=lambda: change_window(self.mmFrame, lsFrame)).grid()
        Button(self.mmFrame, text="Scan Surveys", width=25, command=lambda: change_window(self.mmFrame, ssFrame)).grid()

        self.mmFrame.grid()
        self.mainloop()

class CreateSurvey(Frame):
    def __init__(self, root):
        self.root=root
        super().__init__(root)
        Button(self, text="Back to Menu", width=25, command=self.back_to_menu).grid(row=0, column=0)
        Button(self, text="Save and Print Survey", width=25, command=self.print_survey).grid(row=0, column=1)
        Label(self, text="Create Survey").grid(row=1, columnspan=2)

        Label(self, text="Survey title:").grid(row=2, column=0)
        self.title = Entry(self)
        self.title.grid(row=2, column=1)
        Label(self, text="Subtitle:").grid(row=3, column=0)
        self.subtitle = Entry(self)
        self.subtitle.grid(row=3, column=1)

        Button(self, text="Add Question", command=self.add_question).grid(row=4, column=0)
        Button(self, text="Delete Question", command=self.delete_question).grid(row=4, column=1)
        self.questions = []
    
    def add_question(self):
        i = len(self.questions)
        q = Entry(self)
        q.grid(row=i+5, column=0)
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
        change_window(self, self.root.mmFrame)
    
    def print_survey(self):
        # file naming shenanigans
        filename = self.title.get()
        if filename == "":
            filename = "Survey"
        i = 0
        for f in os.listdir("./print"):
            if f == filename+".pdf" or f == filename+"("+str(i)+")"+".pdf":
                i+=1
        if i:
            filename +="("+str(i)+")"
        
        # build PDF
        def print_questions():  # helper for printing out questions & bubbles
            htmlstr = ""
            bubbles = '''<table>
                            <tr>'''+"".join(["<td>"+str(i)+"</td>" for i in range(1,6)])+'''</tr>
                            <tr>'''+"<td>O</td>"*5+'''</tr>
                        </table>'''
            for q in self.questions:
                htmlstr += '''<tr>
                                <td>'''+q.get()+'''</td>
                                <td>'''+bubbles+'''</td>
                            </tr>'''
            return "<table>"+htmlstr+"</table>"

        HTMLstring = '''
            <h1>'''+self.title.get()+'''</h1>
            <h2>'''+self.subtitle.get()+'''</h2>
            <body>
                <p>Answer the questions in this survey using the following scale of agreement:</p>
                <ul>
                    <li>1 - Strongly disagree</li>
                    <li>2 - Somewhat disagree</li>
                    <li>3 - Neutral</li>
                    <li>4 - Somewhat agree</li>
                    <li>5 - Strongly agree</li>
                </ul>
                '''+print_questions()+'''
            </body>
        '''
        pdfkit.from_string(HTMLstring, "./print/"+filename+".pdf",
            options = { 'page-size': 'Letter',
                        'margin-top': '1in',
                        'margin-right': '1in',
                        'margin-bottom': '1in',
                        'margin-left': '1in'})
        # done
        self.back_to_menu()

class ScanSurvey(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root=root
        Button(self, text="Back to Menu", width=25, command=lambda: change_window(self, root.mmFrame)).grid()
        Label(self, text="Scan Surveys").grid()

class ManageTemplates(Frame):
    def __init__(self, root):
        self.root=root
        super().__init__(root)
        Button(self, text="Back to Menu", width=25, command=lambda: change_window(self, root.mmFrame)).grid()
        Label(self, text="Survey Templates").grid()

Application()
