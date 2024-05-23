import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pdf2image import convert_from_path
import cv2
import numpy as np
from utility import change_window

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
            for row in data:
                print(row)
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

#        cv2.imwrite("./temp/contours.jpg", masked)

        if len(alignment) < 5 + len(bubbles):
            messagebox.showerror("Unexpected format", "Alignment symbols were not detected.")
            self.abort()

        approx = 5  # rounding points

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
        cols = sorted(alignSorted[0:5], key=lambda c: c.x)
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

        return bubbleGrid[::-1]
    
    def abort(self):
        for f in os.listdir("./temp/"):
            os.remove("./temp/"+f)
        change_window(self, self.root.mmFrame)
