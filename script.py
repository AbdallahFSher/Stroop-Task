# Emotional Stroop Test for Migraineurs
# Author: Abdallah Sher
# Last Updated: June 11, 2024
# Sources:
# 1.) https://www.scenegrammarlab.com/databases/bawl-r-database/
# 2.) https://doi.org/10.1186/1471-2377-11-141

import pygame
import pandas as pd
import random
import time

subject = input("Enter Subject ID: ")

# Check if the subject is a migraineur; if so, enter trigger words; mayhaps adjust this based on input from Sebastian
migraine = input("Migraineur? (y/n): ")
if(migraine == "y"):
    migraine = True
    triggerWords = input("Enter trigger words separated by commas: ")
    triggerWords = triggerWords.split(",")
    triggerWords = [word.strip() for word in triggerWords]
    triggerWords = [word.upper() for word in triggerWords]
else:
    migraine = False

xDim = 640
yDim = 480
centerX = xDim/4
centerY = yDim/2
newWord = True
output = open(f"Outputs/{subject}_{time.localtime().tm_year}_{time.localtime().tm_mday}_{time.localtime().tm_mon}.csv", "w")
output.write("Word, Color, Selected Color, Time\n")
count = 0
trigger = False

# 1.) Import the BAWL-R into python
bawlr = pd.read_excel('BAWL-R.xlsx')
negWords = bawlr.query('EMO_MEAN <= -2.5', inplace=False).reset_index(drop=True)
posWords = bawlr.query('EMO_MEAN >= 2.5', inplace=False).reset_index(drop=True)
neuWords = bawlr.query('EMO_MEAN == 0', inplace=False).reset_index(drop=True)



# 2.) Create a pygame window for the task
pygame.init()
screen = pygame.display.set_mode((xDim, yDim))
clock = pygame.time.Clock()
running = True
font = pygame.font.Font(pygame.font.get_default_font(), size=48)

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
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
            if(migraine and random.randint(0, 100) < triggerChance):
                word = random.choice(triggerWords)
                trigger = True
            else:
                word = negWords.iloc[wordInd]['WORD']
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
    
    screen.fill("black")

    text = pygame.font.Font.render(font, word, True, color)
    screen.blit(text, (centerX, centerY))

    if time.time() - start > 2:
        output.write(f"{word}, {color}, NA, NA\n")
        newWord = True

    pygame.display.flip()
    clock.tick(60)

output.close()
pygame.quit()