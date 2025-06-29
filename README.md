# Survey to CSV

Developed by Alan Jessup

## Overview

This application is a simple tool for collecting anonymized data from printed Likert scale surveys. It can be used to generate PDF surveys, and analyze PDF scans of a generated template to aggregate the resulting data into a CSV file.

It was developed for the purpose of gathering course evaluation feedback, following the observation that digital course evaluation forms result in a significantly lower participation rate than paper surveys.

## Installation

Not packaged for distribution.

To use, must have Python 3 with the following packages installed:

- tkinter
- pdfkit
- json
- pathlib
- pdf2image
- cv2
- numpy

Create empty directories labled "out", "temp", and "templates" in same directory with python scripts.

## Usage

To generate a new survey:

- From the main menu, click "Create New Survey".
- Enter a title, subtitle, and instructions if desired, which will be printed at the top of the page.
- Enter each question for the survey, clicking "Add Question" until all questions are listed.
- Click "Save and Print Survey".
- Retrieve the resulting PDF file from the "print" subdirectory.

Print the resulting survey, distribute to students, and scan completed surveys to a PDF file.

- For best results, use a professional scanner such as a flatbed. Phone camera scans may turn out warped and provide inaccurate results.
- Scan one survey per page.

To collect data from surveys:

- From the main menu, click "Scan Surveys".
- Upload the PDF of the completed surveys.
- Click "Scan Selected PDF".
- Collect the resulting CSV file from the "Scans" directory.

Upload the CSV file to the spreadsheet program of your choice to analyze the results.

To modify and reprint or to delete an existing survey template:

- From the main menu, click "Manage Survey Templates".
- Select a survey file, and select an action from the buttons at the top of the window.
