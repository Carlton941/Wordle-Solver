# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 20:09:37 2022

@author: Carlton
"""
import os
import pandas as pd
from functools import reduce
import OpenWordle
from time import sleep

driver = OpenWordle.open_page()

def get_overlay(known, unknown, options, df):
    #Get lists of overlays for each of the below conditions
    #Word should only use letters that appear in the options list or letters 
    overlayOptionsList1 = [(df[index].apply(lambda letter: (letter in options) | (letter == known[index]) | (letter in unknown.values()))) for index in range(1,6)]
    overlayOptionsList2 = [((df[index] != removals[index]) | (removals[index] is None)) for index in range(1,6)]
    
    #Word should not have letters in yellow positions
    # overlayUnknownList1 = [df.apply(lambda row: (letter in row.values) | (letter is None), axis=1) for letter in unknown.values()]
    overlayUnknownList2 = [((df[index] != unknown[index]) | (unknown[index] is None)) for index in range(1,6)]
    
    #Word must keep letters in green positions
    overlayKnownList = [((df[index] == known[index]) | (known[index] is None)) for index in range (1,6)]
    
    #Word should have at least as many copies of a letter as
    #the total number of times that letter appears in unknown + known (yellow + green)
    letterCounts = {}
    [letterCounts.update({letter:sum(letter == x for x in (list(known.values()) + list(unknown.values())))}) for letter in set(list(known.values()) + list(unknown.values())) if letter is not None];
    letterCountOverlayList = [df.apply(lambda row: (sum(letter == x for x in row.values) >= letterCounts[letter]) if letter in options else (sum(letter == x for x in row.values) == letterCounts[letter]), axis=1) for letter in letterCounts]
    
    #Combine each overlay list into one overlay.
    if overlayOptionsList1:
        overlayOptions1 = reduce(lambda x,y: x & y, overlayOptionsList1)
    else:
        overlayOptions1 = [True]*len(df)
        
    if overlayOptionsList2:
        overlayOptions2 = reduce(lambda x,y: x & y, overlayOptionsList2)
    else:
        overlayOptions2 = [True]*len(df)
        
    overlayUnknown1 = [True]*len(df)
        
    if overlayUnknownList2:
        overlayUnknown2 = reduce(lambda x,y: x & y, overlayUnknownList2)
    else:
        overlayUnknown2 = [True]*len(df)
        
    if overlayKnownList:
        overlayKnown = reduce(lambda x,y: x & y, overlayKnownList)
    else:
        overlayKnown = [True]*len(df)
        
    if letterCountOverlayList:
        letterCountOverlay = reduce(lambda x,y: x & y, letterCountOverlayList)
    else:
        letterCountOverlay = [True]*len(df)
        
    #Finally, combine the overlays into one and use it to filter the dataframe
    overlay = overlayOptions1 & overlayOptions2 & overlayUnknown1 & overlayUnknown2 & overlayKnown & letterCountOverlay
    return overlay


#Calculate frequency scores of the letters, then the words
def get_scores(df):
    #positionalScores has a list of fractions for each letter, in each position
    #This can be used to find the word that will refine the options the most
    positionalScores = [df[index].value_counts()/(5*len(df)) for index in range(1,6)]
    
    #totalScores is the total fraction of each letter in any position
    #This can be used to find the word that is most likely to give us a letter
    totalScores = {'a':0, 'b':0, 'c':0, 'd':0, 'e':0, 'f':0, 'g':0, 'h':0, 'i':0, 'j':0, 'k':0, 'l':0, 'm':0, 'n':0, 'o':0, 'p':0, 'q':0, 'r':0, 's':0, 't':0, 'u':0, 'v':0, 'w':0, 'x':0, 'y':0, 'z':0}
    
    #Or, perhaps, maxScores, which uses the max positional score for each letter?
    #This will not bias towards duplicates of particularly common letters.
    #In fact, it will bias against duplicate letters since the word
    #will not get 5 score contributions
    maxScores = {'a':0, 'b':0, 'c':0, 'd':0, 'e':0, 'f':0, 'g':0, 'h':0, 'i':0, 'j':0, 'k':0, 'l':0, 'm':0, 'n':0, 'o':0, 'p':0, 'q':0, 'r':0, 's':0, 't':0, 'u':0, 'v':0, 'w':0, 'x':0, 'y':0, 'z':0}

    for seq in positionalScores:
        for letter in seq.index:
            totalScores[letter] += seq[letter]
            maxScores[letter] = max(maxScores[letter], seq[letter])

        
    #Calculate the net positional and total scores for every word
    df['positionalScore'] = df.apply(lambda x: sum(positionalScores[index-1][x[index]] for index in range(1,6)), axis=1)
    df['totalScore'] = df.apply(lambda x: sum(totalScores[x[index]] for index in range(1,6)), axis=1)
    df['maxScore'] = df.apply(lambda x: sum(maxScores[x[index]] for index in range(1,6) if x[index] not in list(x[:index-1])), axis=1)
    return df
    

#Choose a word to guess
def get_word(df, haveClue, guessedLetters):
    #If no letters are known yet, use the word with the highest totalScore 
    #and also no duplicate letters OR letters that have been guessed so far
    if not haveClue:
        filterFun = (lambda x: all(y not in guessedLetters for y in x))
        key = df[(df.noDupes) & (df.apply(filterFun, axis=1))].totalScore.idxmax()
    #Otherwise, guess the word with the highest positionalScore, ignoring duplicates
    else:
        # key = df.positionalScore.idxmax()
        key = df.maxScore.idxmax()
        
    return df.loc[key, [1,2,3,4,5]]                
                

### Get the word dictionaries
#Read the lists of words and names
words = open('Dictionary.txt')
nameList = open('list of 5-letter names.txt').readlines()
nameListLower = [x.lower()[:-1] for x in nameList]

#Extract only five-letter non-name words without symbols or numbers, and remove newline characters
wordList = [x[:-1].lower() for x in words if (len(x) == 6) & (x not in nameListLower) & (x[:-1].isalpha())]

#Turn the words into 5-key dictionaries
wordDict = [{1:x[0], 2:x[1], 3:x[2], 4:x[3], 5:x[4]} for x in wordList]

#Make a dataframe with one column for each position in the word
df = pd.DataFrame(wordDict)
df['noDupes'] = df.apply(lambda x: len(set(x))==5, axis=1)
df = df.drop_duplicates()

###Do the default first guess based on highest uniqueness-frequency score
options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
guessedLetters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

#Initialize the feedback variables
haveClue = False
guessedLetters = []
known = {1:None, 2:None, 3:None, 4:None, 5:None}
unknown = {1:None, 2:None, 3:None, 4:None, 5:None}
removals = {1:None, 2:None, 3:None, 4:None, 5:None}
success = False

#Loop five times
for guessNum in range(1,7):
    #Get the words' frequency scores
    df = get_scores(df)
    
    #Choose a word to guess
    guess = get_word(df, haveClue, guessedLetters)
    
    #Write the guess to the webpage
    print("\nGuessing '" + reduce(lambda x,y:x+y, guess) + "'...")
    OpenWordle.type_word(guess, driver)
    OpenWordle.submit(driver)
    
    #Get the feedback from the webpage
    known, unknown, removals, success = OpenWordle.read_row(guessNum, driver)
    
    #Check for win or loss condition
    if success:
        print("\nCorrect!")
        break
    elif (guessNum == 6) and (not success):
        print("\nGame over.")
        break
    
    #Record the guessed letters
    [guessedLetters.append(letter) for letter in guess if letter not in guess]
    
    #Remove the non-present letters
    [options.remove(letter) for letter in removals.values() if (letter is not None) and (letter in options)];
    
    #Narrow the search
    overlay = get_overlay(known, unknown, options, df)
    df = df[overlay]
    print("There are {} possible options in list after this guess.".format(len(df)))
    
    #The first time we get a clue, swap haveClue to True
    if any(known.values()) | any (unknown.values()):
        haveClue = True

sleep(3)
driver.close()
            
    






