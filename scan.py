import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pdf2image import convert_from_path
import cv2
import numpy as np
from pathlib import Path
import csv

class ScanSurvey(Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root=root
        Button(self, text="Back to Menu", width=25, command=lambda: self.root.change_window(self)).grid()
        Label(self, text="Scan Surveys").grid()
        Button(self, text="Upload PDF", width=25, command=self.select_file).grid()
        self.scanButton = Button(self, text="Scan selected PDF", width=25, command=self.scan_pages)
        self.selected = ""
    
    def select_file(self):
        self.selected = filedialog.askopenfilename()
        self.scanButton.grid()
    
    def scan_pages(self):
        pages = convert_from_path(self.selected)
        failedPages = {}
        dataSummary = []
        for k, page in enumerate(pages, 1):
            f = Path("./temp/page"+str(k)+".jpg")
            page.save(f, "JPEG")
            data = self.scan_image(f)
            if type(data) == str:
                failedPages[str(k)] = data
                dataSummary.append(None)
            else:
                dataSummary.append(data)
            os.remove(f)
        
        with open(Path("./out/" + Path(self.selected).stem + ".csv"), "w") as f:
            write = csv.writer(f)
            for block in dataSummary:
                if block == None:
                    write.writerow(["No data"])
                else:
                    csvRow = []
                    for row in block:
                        if row.count(1) == 1:
                            answer = row.index(1) + 1
                            csvRow.append(answer)
                        else: # otherwise either no answer or multiple answers selected, may require review
                            csvRow.append("?")
                    write.writerow(csvRow)

        if failedPages != {}:
            messagebox.showerror("Scanning error", "Unable to read the following pages:\n"+"\n".join([f+": "+failedPages[f] for f in failedPages.keys()]))

        self.root.change_window(self)

    def scan_image(self, f):
        class Bubble:  # local helper data structure limited to scope of scan_image method
            def __init__(self, x, y, contour):
                self.x = x  # coordinates
                self.y = y
                self.contour = contour
                self.cluster = False  # flag for clustered contours indicate messily-filled in answer

        # prepare image
        image = cv2.imread(f.absolute().as_posix())
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # use contours to detect table quadrants
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) < 3:
            return "Failed to find bubble box contour."
        bubbleBox = sorted(contours, key=lambda c: cv2.contourArea(c))[-4]  # third-largest contour
        cv2.drawContours(image, [bubbleBox], 0, (0, 255, 0), 5)
#        cv2.imwrite("./temp/"+str(f.stem)+"-contours.jpg", image)

        # mask irrelevant quadrants
        mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.rectangle(mask, cv2.boundingRect(bubbleBox), 255, -1)
        masked = cv2.bitwise_and(image, image, mask=mask)

        # detect filled bubbles (blurred)
        blurred = cv2.blur(masked, (10,10))
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # convert to bubble objects
        contourObjs = []
        for c in contours[1::]:
            if cv2.contourArea(c, True) < 0:  # duplicate contour indicating hole/uneven filling
                continue
            # find center
            M = cv2.moments(c)
            if M['m00'] != 0.0:
                x = int(M['m10']/M['m00'])
                y = int(M['m01']/M['m00'])
                contourObjs.append(Bubble(x, y, c))

        # remove repeat/clustered contours caused by uneven filling
        contourObjs = sorted(contourObjs, key=lambda c: c.x+c.y)
        approx = 20  # rounding points
        n = len(contourObjs)
        i = 0
        while i < n-1:
            c1 = contourObjs[i]
            c2 = contourObjs[i+1]
            if abs(c1.x-c2.x) <= approx and abs(c1.y-c2.y) <= approx:
                del contourObjs[i+1]
                c1.cluster = True
                n -= 1
            else:
                i += 1

        # sort contours into bubbles and alignment symbols
        bubbles = []
        alignment = []
        for c in contourObjs:
            if len(c.contour) < 20 and not c.cluster:
                alignment.append(c)
            else:
                bubbles.append(c)
        
        # confirm alignment contours align to grid (else should be bubble)
        n = len(alignment)
        i = 0
        medX = sorted(alignment, key=lambda c: c.x)[-1].x
        medY = sorted(alignment, key=lambda c: c.y)[-1].y
        while i < n-1:
            a = alignment[i]
            if abs(a.x-medX) > approx and abs(a.y-medY) > approx:
                del alignment[i]
                bubbles.append(a)
                n -= 1
            else:
                i += 1

        # draw contours to temp file for debugging purposes
        for a in alignment:
            cv2.drawContours(masked, [a.contour], 0, (0, 0, 255), 5)
            cv2.putText(masked, str(len(a.contour)), (a.x-50,a.y), 0, 1, (0, 0, 0), 2)
        for b in bubbles:
            cv2.drawContours(masked, [b.contour], 0, (0, 255, 0), 5)
            cv2.putText(masked, str(len(b.contour)), (b.x-50,b.y), 0, 1, (0, 0, 0), 2)
#        cv2.imwrite("./temp/"+str(f.stem)+"-mask.jpg", masked)

        # build grid
        alignSorted = sorted(alignment, key=lambda c: c.y)[::-1]
        cols = sorted(alignSorted[0:5], key=lambda c: c.x)
        rows = alignSorted[5::]
        for r in rows:  # format error check
            if cols[-1].x > r.x:
                return "Alignment symbols not detected properly at position 2."
        
        bubbleGrid = [[0]*5 for i in range(len(rows))]

        for b in bubbles:
            r,c = None, None
            minXDif, minYDif = None, None
            for i in range(len(rows)):
                if minYDif==None or abs(b.y - rows[i].y) <= minYDif:
                    minYDif = abs(b.y - rows[i].y)
                if abs(b.y - rows[i].y) <= approx:
                    r = i
                    break
            for j in range(5):
                if minXDif==None or abs(b.x - cols[j].x) <= minXDif:
                    minXDif = abs(b.x - cols[j].x)
                if abs(b.x - cols[j].x) <= approx:
                    c = j
                    break
            if r==None or c==None:  # grid error check
                cv2.drawContours(masked, [b.contour], 0, (255, 0, 0), 5)
                return "Bubbles did not match grid by "+str(minXDif)+", "+str(minYDif)+" points."
            bubbleGrid[r][c] = 1

        return bubbleGrid[::-1]
