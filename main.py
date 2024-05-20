import os
from tkinter import *
from tkinter import filedialog
import pdfkit
import cv2
from pdf2image import convert_from_path

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
            labels = "".join(["<td style='text-align: center'>"+str(i)+"</td>" for i in range(1,6)])
            bubbles = "<td style='font-size: 12pt'>&#x25EF</td>"*5
            alignmentSquares = "<tr><td></td>"+"<td style='text-align: center'>&#x25A0</td>"*5+"</tr>"

            htmlstr = "<tr><td></td>"+labels

            for q in self.questions:
                htmlstr += '''<tr>
                                <td>'''+q.get()+'''</td>
                                '''+bubbles+'''
                                <td>&#x25C0</td>
                            </tr>'''
            
            htmlstr += alignmentSquares
            return "<table style='border-spacing: 20px'>"+htmlstr+"</table>"

        HTMLstring = '''
            <h1>'''+self.title.get()+'''</h1>
            <h2>'''+self.subtitle.get()+'''</h2>
            <body>
                <p>Answer the questions in this survey using the following scale of agreement:</p>
                <ul style="list-style-type:none">
                    <li>1 - Strongly disagree</li>
                    <li>2 - Somewhat disagree</li>
                    <li>3 - Neutral</li>
                    <li>4 - Somewhat agree</li>
                    <li>5 - Strongly agree</li>
                </ul>
                <p>Make sure to fill bubbles in entirely in dark pen or pencil, and do not fill outside the bubbles.</p>
                '''+print_questions()+'''
            </body>
        '''
        pdfkit.from_string(HTMLstring, "./print/"+filename+".pdf",
            options = { 'page-size': 'Letter',
                        'margin-top': '1in',
                        'margin-right': '1in',
                        'margin-bottom': '1in',
                        'margin-left': '1in'},
        )
        self.back_to_menu()

class ScanSurvey(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root=root
        Button(self, text="Back to Menu", width=25, command=lambda: change_window(self, root.mmFrame)).grid()
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
        for f in os.listdir("./temp"):
            data = self.scan_image(cv2.imread(f))
            print(data)

    def scan_image(self, image):
        # threshold for gray
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # use contours to detect alignment shapes & filled bubbles
        tri = []
        sqr = []
        circ = []
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours[1::]:  # ignore first contour which is full image
            approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True) 
            cv2.drawContours(self.image, [contour], 0, (0, 0, 255), 5) 
            # find center of shape
            M = cv2.moments(contour)
            if M['m00'] != 0.0:
                x = int(M['m10']/M['m00'])
                y = int(M['m01']/M['m00'])
            if len(approx) == 3:    # alignment triangles (along right edge)
                tri.append((x, y))
            if len(approx) == 4:    # alignment squares (along bottom edge)
                sqr.append((x, y))
            else:                   # circles (filled bubbles)
                circ.append((x, y))

        assert len(sqr) == 5

        # calculate vertical boundaries between rows/columns
        tri = sorted(tri, key=lambda c: c[1])
        rows = [tri[i][1]+(tri[i+1][1]-tri[i][1])/2 for i in range(len(tri)-2)]
        sqr = sorted(sqr, key=lambda c: c[0])
        cols = [sqr[i][0]+(sqr[i+1][0]-sqr[i][0])/2 for i in range(3)]

        # transfer filled bubbles to array
        data = [[0,0,0,0,0]*len(tri)]
        q = 0  # row (question) index
        for x, y in sorted(circ, key=lambda c: c[1]):
            while y > rows[q]:
                q += 1
            if x < cols[0]:
                data[q][0] = 1
            elif x < cols[1]:
                data[q][1] = 1
            elif x < cols[2]:
                data[q][2] = 1
            elif x < cols[3]:
                data[q][3] = 1
            else:
                data[q][4] = 1

        return data

class ManageTemplates(Frame):
    def __init__(self, root):
        self.root=root
        super().__init__(root)
        Button(self, text="Back to Menu", width=25, command=lambda: change_window(self, root.mmFrame)).grid()
        Label(self, text="Survey Templates").grid()

Application()
