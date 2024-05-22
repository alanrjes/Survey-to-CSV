import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import pdfkit
import cv2
from pdf2image import convert_from_path
import numpy as np

# global utility function:
def change_window(currentFrame, nextFrame):
    currentFrame.grid_forget()
    nextFrame.grid()
    try:
        nextFrame.scanButton.grid_forget()
    except AttributeError:
        pass  # if it's not there, no need to hide it

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
        Label(self, text="Instructions:").grid(row=4, column=0)
        self.instructions = Entry(self)
        self.instructions.grid(row=4, column=1)

        Button(self, text="Add Question", command=self.add_question).grid(row=5, column=0)
        Button(self, text="Delete Question", command=self.delete_question).grid(row=5, column=1)
        self.questions = []
    
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
        change_window(self, self.root.mmFrame)
    
    def print_survey(self):
        # file naming shenanigans
        filename = self.title.get()
        if filename == "":
            filename = "Survey"
        i = 1
        usedNames = os.listdir("./print")
        tempName = filename
        while tempName+".pdf" in usedNames:
            tempName = filename + "("+str(i)+")"
            i+=1
        filename = tempName
        
        # build PDF
        def print_questions():  # helper for printing out questions & bubbles
            scale = ["Strongly Disagree", "Somewhat Disagree", "Neutral", "Somewhat Agree", "Strongly Agree"]
            labels = "".join(["<td style='padding: 5px; text-align: center; border-bottom: 1px solid black'>"+s+"</td>" for s in scale]) + "<td style='border-bottom: 1px solid black'>"
            bubbles = "<td style='padding: 5px; text-align: center; font-size: 12pt'>&#x25EF</td>"*5 + "<td style='padding: 5px; font-size: 12pt'>&#x25C2</td>"

            htmlstr = "<tr><td style='padding: 5px; border-right: 1px solid black; border-bottom: 1px solid black'><b>Questions</b></td>"+labels

            for q in self.questions:
                htmlstr += '''<tr style="padding: 5px">
                                <td style="padding: 5px; width: 100%; border-right: 1px solid black">'''+q.get()+'''</td>
                                '''+bubbles+'''
                            </tr>'''
            htmlstr += "<tr style='border-right: 1px solid black; border-left: 1px solid black; border-bottom: 1px solid black'><td style='border-right: 1px solid black'></td>"+"<td style='text-align: center'>&#x25B4</td>"*5+"<td></td></tr>"
            
            return "<table style='width: 100%; border-collapse: collapse; border: 1px solid black'>"+htmlstr+"</table>"

#                <p>Answer the questions in this survey using the following scale of agreement:</p>
#                <ul style="list-style-type:none">
#                    <li>1 - Strongly disagree</li>
#                    <li>2 - Somewhat disagree</li>
#                    <li>3 - Neutral</li>
#                    <li>4 - Somewhat agree</li>
#                    <li>5 - Strongly agree</li>
#                </ul>

        HTMLstring = '''
            <h1>'''+self.title.get()+'''</h1>
            <h2>'''+self.subtitle.get()+'''</h2>
            <body>
                <p>'''+self.instructions.get()+'''</p>
                '''+print_questions()+'''
            </body>
        '''
        pdfkit.from_string(HTMLstring, "./print/"+filename+".pdf",
            options = { 'page-size': 'Letter',
                        'margin-top': '0.5in',
                        'margin-right': '0.5in',
                        'margin-bottom': '0.5in',
                        'margin-left': '0.5in'},
        )
        self.back_to_menu()

class ScanSurvey(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root=root
        Button(self, text="Back to Menu", width=25, command=self.abort).grid()
        Label(self, text="Scan Surveys").grid()
        Button(self, text="Upload PDF", width=25, command=self.select_file).grid()
        self.scanButton = Button(self, text="Scan selected PDF", width=25, command=self.scan_pages)
    
    def select_file(self):
        filename = filedialog.askopenfilename()
        pages = convert_from_path(filename)
        for count, page in enumerate(pages):
            page.save(f'./temp/page{count}.jpg', 'JPEG')
        self.scanButton.grid()
    
    def scan_pages(self):
        for f in os.listdir("./temp/"):
            data = self.scan_image(f)
            os.remove("./temp/"+f)
            print(data)
        # do something to save to CSV
        change_window(self, self.root.mmFrame)

    def scan_image(self, f):
        class Bubble:  # local helper data structure limited to scope of scan_image method
            def __init__(self, x, y, contour):
                self.x = x  # coordinates
                self.y = y
                self.contour = contour

        # prepare image
        image = cv2.imread("./temp/"+f)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # use contours to detect table quadrants
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        bubbleBox = sorted(contours, key=lambda c: cv2.contourArea(c))[-4]  # third-largest contour

        # mask irrelevant quadrants
        mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.rectangle(mask, cv2.boundingRect(bubbleBox), 255, -1)
        masked = cv2.bitwise_and(image, image, mask=mask)

        # detect filled bubbles (blurred)
        blurred = cv2.blur(masked, (10,10))
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        bubbles = []
        alignment = []
        for c in contours[1::]:
            if cv2.contourArea(c, True) < 0:  # duplicate contour indicating hole/uneven filling
                continue
            # find center
            M = cv2.moments(c)
            if M['m00'] != 0.0:
                x = int(M['m10']/M['m00'])
                y = int(M['m01']/M['m00'])
                if len(c) < 20:  # is an alignment triangle
                    alignment.append(Bubble(x,y,c))
                    cv2.drawContours(masked, [c], 0, (0, 0, 255), 5)
                else:  # is a filled bubble
                    bubbles.append(Bubble(x,y,c))
                    cv2.drawContours(masked, [c], 0, (0, 255, 0), 5)

        cv2.imwrite("./temp/contours.jpg", masked)

        approx = 4  # rounding points

        # discard duplicate contours resulting from uneven filling
        n = len(bubbles)
        i = 0
        while i < n-1:
            c1 = bubbles[i]
            c2 = bubbles[i+1]
            if abs(c1.x-c2.x) <= approx and abs(c1.y-c2.y) <= approx:
                del bubbles[i+1]
                n -= 1
            i += 1

        # build grid
        alignSorted = sorted(alignment, key=lambda c: c.y)[::-1]
        cols = alignSorted[0:5]
        rows = alignSorted[5::]
        for r in rows:  # format error check
            if cols[-1].x > r.x:
                messagebox.showerror("Unexpected format", "Alignment symbols were not detected correctly.")
                self.abort()
        
        bubbleGrid = [[0]*5 for i in range(len(rows))]

        for b in bubbles:
            r,c = None, None
            for i in range(len(rows)):
                if abs(b.y - rows[i].y) <= approx:
                    r = i
                    break
            for j in range(5):
                if abs(b.x - cols[j].x) <= approx:
                    c = j
                    break
            if r==None or c==None:  # grid error check
                messagebox.showerror("Irregular grid", "Filled bubbles did not match alignment grid.")
                self.abort()
            bubbleGrid[r][c] = 1

#        os.remove("./temp/contours.jpg")
        return bubbleGrid[::-1]
    
    def abort(self):
        for f in os.listdir("./temp/"):
            os.remove("./temp/"+f)
        change_window(self, self.root.mmFrame)

class ManageTemplates(Frame):
    def __init__(self, root):
        self.root=root
        super().__init__(root)
        Button(self, text="Back to Menu", width=25, command=lambda: change_window(self, root.mmFrame)).grid()
        Label(self, text="Survey Templates").grid()

Application()
