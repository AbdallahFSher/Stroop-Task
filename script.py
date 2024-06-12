# Emotional Stroop Test for Migraineurs
# Author: Abdallah Sher
# Last Updated: June 12, 2024
# Version 1.05
# Sources:
# 1.) https://www.scenegrammarlab.com/databases/bawl-r-database/
# 2.) https://doi.org/10.1186/1471-2377-11-141

import pygame
import pandas as pd
import random
import time
import win32gui
import tkinter as tk
from tkinter import ttk

running = False
migraineBool = False

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

# xDim = 640
# yDim = 480
# centerX = xDim/2
# centerY = yDim/2

# Define variables
newWord = True
subjectStr = subjectTk.get()
output = open(f"Outputs/{subjectStr}_{time.localtime().tm_year}_{time.localtime().tm_mday}_{time.localtime().tm_mon}.csv", "w")
output.write("Word, Color, Selected Color, Time, Correct?, Trigger?\n")
count = 0
trigger = False

# 1.) Import the BAWL-R into python
bawlr = pd.read_excel('BAWL-R.xlsx')
negWords = bawlr.query('EMO_MEAN <= -2.5', inplace=False).reset_index(drop=True)
posWords = bawlr.query('EMO_MEAN >= 2.5', inplace=False).reset_index(drop=True)
neuWords = bawlr.query('EMO_MEAN == 0', inplace=False).reset_index(drop=True)


if(running):
    triggerWords = triggerWordsTK.get()
    triggerWords = triggerWords.split(",")
    triggerWords = [word.strip() for word in triggerWords]
    triggerWords = [word.upper() for word in triggerWords]
    # 2.) Create a pygame window for the task
    pygame.init()
    screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    pygame.display.set_caption("Emotional Stroop Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(pygame.font.get_default_font(), size=72)
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()
    bringToFront("Emotional Stroop Test")

# Main Loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        if event.type == pygame.KEYDOWN:
            end = time.time()
            # Check the selected color
            if(event.key == pygame.K_j):
                selectedColor = "red"
            elif(event.key == pygame.K_k):
                selectedColor = "blue"
            elif(event.key == pygame.K_l):
                selectedColor = "green"
            else:
                selectedColor = "NA"

            # Check if the selected color is correct    
            if(selectedColor == color):
                correct = True
            else:
                correct = False
            output.write(f"{word}, {color}, {selectedColor}, {end - start}, {correct}, {trigger}\n")
            newWord = True
            screen.fill("black")
            pygame.display.flip()       

    if(newWord):
        time.sleep(0.5)
        wordType = random.randint(0, 2)
        if(wordType == 0):
            # Negative Word
            triggerChance = 50
            wordInd = random.randint(0, negWords.shape[0] - 1)
            if(migraineBool and random.randint(0, 100) < triggerChance):
                word = random.choice(triggerWords)
                trigger = True
            else:
                word = negWords.iloc[wordInd]['WORD']
                trigger = False
        elif(wordType == 1):
            # Neutral Word
            wordInd = random.randint(0, neuWords.shape[0] - 1)
            word = neuWords.iloc[wordInd]['WORD']
        elif(wordType == 2):
            # Positive Word
            wordInd = random.randint(0, posWords.shape[0] - 1)
            word = posWords.iloc[wordInd]['WORD']
        newWord = False
        color = random.choice(["red", "blue", "green"])
        start = time.time()
        count += 1

    if(count == 108):
        running = False

    text = pygame.font.Font.render(font, word, True, color)
    textRect = text.get_rect(center=screen.get_rect().center)
    screen.blit(text, textRect)

    if time.time() - start > 2:
        output.write(f"{word}, {color}, NA, NA, NA, NA\n")
        newWord = True
        screen.fill("black")

    pygame.display.flip()
    clock.tick(60)

output.close()
pygame.quit()