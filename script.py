# Emotional Stroop Test for Migraineurs
# Author: Abdallah Sher
# Last Updated: June 17, 2024
# Version 1.2
# Sources:
# 1.) https://www.scenegrammarlab.com/databases/bawl-r-database/
# 2.) https://doi.org/10.1186/1471-2377-11-141

from psychopy import core, visual, event
from psychopy.hardware import keyboard
import numpy as np
from pylsl import StreamInfo, StreamOutlet
import screeninfo
import pandas as pd
import random
import time
import win32gui
import tkinter as tk
from tkinter import ttk

#Important globals
running = False
migraineBool = False
kb = keyboard.Keyboard()

# Create a LSL stream for the trigger words
triggerInfo = StreamInfo(name='TriggerStream', type='Markers', channel_count=1, channel_format='int32', source_id='Emotional_Stroop_Marker_Stream') # type: ignore
triggerOutlet = StreamOutlet(triggerInfo)

# Function to bring the window to the front
def windowsEnumerationHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

results = []
top_windows = []
win32gui.EnumWindows(windowsEnumerationHandler, top_windows)

def bringToFront(windowName):
    for i in top_windows:
        if i[1] == windowName:
            win32gui.ShowWindow(i[0], 5)
            win32gui.SetForegroundWindow(i[0])
            break

# Function to show the trigger words entry based on value of migraineVar
def showTriggerEntry(*arg):
    global migraineBool
    if(migraineVar.get() == "No"):
        triggerWordsLabel.grid_remove()
        triggerWordsEntry.grid_remove()
        inputWindow.geometry("300x200")
        migraineBool = False
    else:
        triggerWordsLabel.grid(column=0, row=2, padx=10, pady=10)
        triggerWordsEntry.grid(column=1, row=2, padx=10, pady=10)
        inputWindow.geometry("300x250")
        migraineBool = True

# Function to start the test
def beginTest(event):
    global running
    running = True
    inputWindow.destroy()


# Create a tkinter window to get the subject ID and migraine status
inputWindow = tk.Tk()
inputWindow.title("Start Stroop Test")
inputWindow.geometry("300x200")
inputWindow.resizable(False, False)

frm = ttk.Frame(inputWindow)
frm.grid(column=0, row=0, padx=10, pady=30)

lbl = ttk.Label(frm, text="Enter Subject ID:")
lbl.grid(column=0, row=0)
subjectTk = tk.StringVar()
subject = ttk.Entry(frm, textvariable=subjectTk)
subject.grid(column=1, row=0, padx=10, pady=10)

migraine = ttk.Label(frm, text="Migraineur?")
migraine.grid(column=0, row=1, padx=10, pady=10)
migraineVar = tk.StringVar()
migraineVar.set("No")
migraine = ttk.Combobox(frm, textvariable=migraineVar)
migraine['values'] = ("Yes", "No")
migraine.grid(column=1, row=1)
migraine.current()

triggerWordsLabel = ttk.Label(frm, text="Enter Trigger Words\n(separated by ',') :")
triggerWordsTK = tk.StringVar()
triggerWordsEntry = ttk.Entry(frm, textvariable=triggerWordsTK)
migraineVar.trace_add("write", showTriggerEntry)

startButton = ttk.Button(frm, text="Start Test")
startButton.grid(column=1, row=3, padx=10, pady=10)
startButton.bind("<Button-1>", lambda event: beginTest(event))

inputWindow.mainloop()

# Define variables
newWord = True
subjectStr = subjectTk.get()
output = open(f"Outputs/{subjectStr}_{time.localtime().tm_year}_{time.localtime().tm_mday}_{time.localtime().tm_mon}.csv", "w")
count = 0
trigger = False
triggerChance = 50 # Chance of trigger word; maybe this should be adjusted based on the number of trigger words

# 1.) Import the BAWL-R into python
bawlr = pd.read_excel('BAWL-R.xlsx')
negWords = bawlr.query('EMO_MEAN <= -2.5', inplace=False).reset_index(drop=True)
posWords = bawlr.query('EMO_MEAN >= 2.5', inplace=False).reset_index(drop=True)
neuWords = bawlr.query('EMO_MEAN == 0', inplace=False).reset_index(drop=True)


if(running):
    training = True
    triggerWords = triggerWordsTK.get()
    triggerWords = triggerWords.split(",")
    triggerWords = [word.strip() for word in triggerWords]
    triggerWords = [word.upper() for word in triggerWords]
    output.write("Trigger Words Used:,")
    for word in triggerWords:
        output.write(f"{word},")
    output.write("\n")
    output.write("Word, Color, Selected Color, Time, Correct?, Trigger?, Word Type\n")
    # 2.) Create a window for the task
    SCREEN_WIDTH = screeninfo.get_monitors()[0].width
    SCREEN_HEIGHT = screeninfo.get_monitors()[0].height
    window = visual.Window(size=(SCREEN_WIDTH, SCREEN_HEIGHT), fullscr=True, allowGUI=False, allowStencil=False, monitor='display1', color=[-1,-1,-1], colorSpace='rgb', blendMode='avg', useFBO=False, waitBlanking = True, units="pix")
    bringToFront("Emotional Stroop Test")
    visual.TextStim(window, text="40 Training Trials", color="white", height=50).draw()
    window.flip()
    time.sleep(2)



# Main Loop
while running:
    # Setting the new word
    if(newWord):
        time.sleep(0.5) # Interstimulus interval
        wordType = random.choice(["positive", "neutral", "negative"])
        if(wordType == "negative"):
            # Negative Word
            wordInd = random.randint(0, negWords.shape[0] - 1)
            if(migraineBool and random.randint(0, 100) < triggerChance):
                word = random.choice(triggerWords)
                trigger = True
            else:
                word = negWords.iloc[wordInd]['WORD']
                trigger = False
        elif(wordType == "neutral"):
            # Neutral Word
            wordInd = random.randint(0, neuWords.shape[0] - 1)
            word = neuWords.iloc[wordInd]['WORD']
        elif(wordType == "positive"):
            # Positive Word
            wordInd = random.randint(0, posWords.shape[0] - 1)
            word = posWords.iloc[wordInd]['WORD']
        newWord = False
        color = random.choice(["red", "blue", "green"])
        start = time.time()
        count += 1

    if(count == 148):
        running = False
        break

    text = visual.TextStim(window, text=word, color=color, height=100)
    text.draw()
    window.flip()

    # Get user input this loop
    keys = event.getKeys()
    
    # If keys is not empty (User pressed something)
    if keys:
        # Event handling
        if 'escape' in keys:
            running = False
        # Check the selected color
        if 'j' in keys:
            end = time.time()
            selectedColor = "red"
        elif 'k' in keys:
            end = time.time()
            selectedColor = "blue"
        elif 'l' in keys:
            end = time.time()
            selectedColor = "green"
        else:
            end = time.time()
            selectedColor = "NA"

                # Check if the selected color is correct    
        if(selectedColor == color):
            correct = True
        else:
            correct = False
        if not training:
            output.write(f"{word}, {color}, {selectedColor}, {end - start}, {correct}, {trigger}, {wordType}\n")
        # 0: Trigger
        # 1: Negative
        # 2: Neutral
        # 3: Positive
        if(trigger):
            triggerOutlet.push_sample([0])
        elif wordType == "negative":
            triggerOutlet.push_sample([1])
        elif wordType == "neutral":
            triggerOutlet.push_sample([2])
        elif wordType == "positive":
            triggerOutlet.push_sample([3])
        newWord = True
        window.color = [-1, -1, -1]
        window.flip() 

    # If the user does not respond in 2 seconds, move to the next word
    if time.time() - start > 2:
        if not training:
            output.write(f"{word}, {color}, NA, NA, NA, NA\n")
        newWord = True
        window.color = [-1, -1, -1]
        window.flip()

    if count == 40:
        training = False
        newWord = True
        window.color = [-1, -1, -1]
        dialogue = visual.TextStim(window, text="Training Complete! Beginning in...", color="white", height=50)
        dialogue.draw()
        for i in range(10, 0, -1):
            dialogue.draw()
            visual.TextStim(window, text=str(i), color="white", height=100, pos=(dialogue.pos[0],dialogue.pos[1]-100)).draw()
            window.flip()
            time.sleep(1)

output.close()
core.quit()