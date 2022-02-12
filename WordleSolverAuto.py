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

# os.chdir('C:\\Users\\a47pqzz\\OneDrive - 3M\\Documents\\Wordle Solver')
driver = OpenWordle.open_page()

def get_overlay(known, unknown, options, df):
    #Get lists of overlays for each of the below conditions
    #Word should only use letters that appear in the options list
    overlayOptionsList1 = [(df[index].apply(lambda letter: (letter in options) | (letter == known[index]))) for index in range(1,6)]
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
    letterCountOverlayList = [df.apply(lambda row: sum(letter == x for x in row.values) >= letterCounts[letter], axis=1) for letter in letterCounts]
    
    #Combine each overlay list into one overlay.
    if overlayOptionsList1:
        overlayOptions1 = reduce(lambda x,y: x & y, overlayOptionsList1)
    else:
        overlayOptions1 = [True]*len(df)
        
    if overlayOptionsList2:
        overlayOptions2 = reduce(lambda x,y: x & y, overlayOptionsList2)
    else:
        overlayOptions2 = [True]*len(df)
        
    # if overlayUnknownList1:
    #     overlayUnknown1 = reduce(lambda x,y: x & y, overlayUnknownList1)
    # else:
    #     overlayUnknown1 = [True]*len(df)
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

### Get the word dictionaries
#Read the lists of words and names
wordList = open('Dictionary.txt')
nameList = open('list of 5-letter names.txt').readlines()
nameListLower = [x.lower()[:-1] for x in nameList]

#Extract only five-letter non-name words without symbols or numbers, and remove newline characters
wordList2 = [x[:-1].lower() for x in wordList if (len(x) == 6) & (x not in nameListLower) & (x[:-1].isalpha())]

#Turn the words into 5-key dictionaries
wordDict = [{1:x[0], 2:x[1], 3:x[2], 4:x[3], 5:x[4]} for x in wordList2]

#Make a dataframe with one column for each position in the word
df = pd.DataFrame(wordDict)

#The (approximate) frequencies of the letters in English
#These will act as proxies for value
scores = {'e':.111607, 'a':.084966, 'r':.075809, 'i':.075448, 'o':.071635, 't':.069509, 'n':.066544, 's':.057351, 'l':.054893, 'c':.045388, 'u':.036308, 'd':.033844, 'p':.031671, 'm':.030129, 'h':.030034, 'g':.024705, 'b':.02720, 'f':.018121, 'y':.017779, 'w':.012899, 'k':.011016, 'v':.010074, 'x':.002902, 'z':.002722, 'j':.001965, 'q':.01962}

#Give each word in the dataframe a cumulative score
df['score'] = [sum(scores[word[pos]] for pos in range(5)) for word in wordList2]
ufdf = df.loc[:]
ufdf['ufScore'] = [(sum((scores[word[pos]] if (word[pos] not in word[:pos]) else 0) for pos in range(5))) for word in wordList2]

df = df.sort_values(by='score', ascending=False)
ufdf = ufdf.sort_values(by='ufScore', ascending=False)
df = df[df.duplicated(keep='last')]
ufdf = ufdf[ufdf.duplicated(keep='last')]

###Do the default first guess based on highest uniqueness-frequency score
options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
ufOptions = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

guess = ufdf.iloc[0,:5]
[ufOptions.remove(letter) for letter in guess if letter in ufOptions];
print("Gathering initial feedback with '{}'.\n".format(reduce(lambda x,y: x+y, guess)))
OpenWordle.type_word(ufdf.iloc[0,:5],driver)
OpenWordle.submit(driver)


#Loop five times
correctLetters = 0;
for guessNum in range(1,6):
    #Get the feedback
    known, unknown, removals, success = OpenWordle.read_row(guessNum, driver)
    [options.remove(letter) for letter in removals.values() if (letter is not None) and (letter in options)];
    
    #Check for win or loss condition
    # if success:
    #     print("Correct!")
    #     break
    # elif (guessNum == 6) and (not success):
    #     print("Game over.")
    #     break
    
    #Narrow the search
    overlay = get_overlay(known, unknown, options, df)
    df = df[overlay]
    print("There are {} possible options in list after filtering.".format(len(df)))
    
    #Narrow the ufdf
    ufOverlayList = [(ufdf[index].apply(lambda letter: letter in ufOptions)) for index in range(1,6)]
    ufOverlay = reduce(lambda x,y: x & y, ufOverlayList)
    ufdf = ufdf[ufOverlay]
    
    #Update correct letter count
    correctLetters += (len([x for x in known.values() if x is not None]) + len([x for x in unknown.values() if x is not None]))
    
    #If we don't have enough information, gather more data by guessing letters we haven't tried yet
    #Otherwise, try to guess the correct word.
    if correctLetters <= 1:
        guess = ufdf.iloc[0,:5]
        print("Not enough information. Gathering more feedback with '{}'.\n".format(reduce(lambda x,y: x+y, guess)))
    else:
        guess = df.iloc[0,:5]
        print("Attempting to guess answer with '{}'.\n".format(reduce(lambda x,y: x+y, guess)))        
    
    #Update ufOptions and submit
    [ufOptions.remove(letter) for letter in guess if letter in ufOptions];
    OpenWordle.type_word(guess, driver)
    OpenWordle.submit(driver)

# sleep(5)
# driver.close()
            
    






