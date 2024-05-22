from tkinter import *

def change_window(currentFrame, nextFrame):
    currentFrame.grid_forget()
    nextFrame.grid()
    try:
        nextFrame.scanButton.grid_forget()
    except AttributeError:
        pass  # if it's not there, no need to hide it
