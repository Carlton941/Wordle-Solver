# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 20:09:37 2022

@author: Carlton
"""
import os
import pandas as pd
from functools import reduce
import OpenWordle

os.chdir('C://Users//Carlton//Documents//Wordle')
driver = OpenWordle.open_page()

def get_overlay(known, unknown, options, df):
    #Get lists of overlays for each of the three conditions
    overlayOptionsList = [(df[index].apply(lambda letter: letter in options)) for index in range(1,6)]
    overlayUnknownList1 = [df.apply(lambda row: (letter in row.values) | (letter is None), axis=1) for letter in unknown.values()]
    overlayUnknownList2 = [((df[index] != unknown[index]) | (unknown[index] is None)) for index in range(1,6)]
    overlayKnownList = [((df[index] == known[index]) | (known[index] is None)) for index in range (1,6)]
    
    #Combine each overlay list into one overlay.
    if overlayOptionsList:
        overlayOptions = reduce(lambda x,y: x & y, overlayOptionsList)
    else:
        overlayOptions = [True]*len(df)
        
    if overlayUnknownList1:
        overlayUnknown1 = reduce(lambda x,y: x & y, overlayUnknownList1)
    else:
        overlayUnknown1 = [True]*len(df)
        
    if overlayUnknownList2:
        overlayUnknown2 = reduce(lambda x,y: x & y, overlayUnknownList2)
    else:
        overlayUnknown2 = [True]*len(df)
        
    if overlayKnownList:
        overlayKnown = reduce(lambda x,y: x & y, overlayKnownList)
    else:
        overlayKnown = [True]*len(df)
    
    #Finally, combine the overlays into one and use it to filter the dataframe
    overlay = overlayOptions & overlayUnknown1 & overlayUnknown2 & overlayKnown
    return overlay

### Get the word dictionaries
#Read the lists of words and names
wordList = open('list of English words.txt').readlines()
nameList = open('list of 5-letter names.txt').readlines()
nameListLower = [x.lower() for x in nameList]

#Extract only five-letter words that are not just names and remove newline characters
wordList2 = [x[:-1] for x in wordList if (len(x) == 6) & (x not in nameListLower)]

#Turn the words into 5-key dictionaries
wordDict = [{1:x[0], 2:x[1], 3:x[2], 4:x[3], 5:x[4]} for x in wordList2]

#Make a dataframe with one column for each position in the word
df = pd.DataFrame(wordDict)

#The (approximate) frequencies of the letters in English
#These will act as proxies for value
scores = {'e':.111607, 'a':.084966, 'r':.075809, 'i':.075448, 'o':.071635, 't':.069509, 'n':.066544, 's':.057351, 'l':.054893, 'c':.045388, 'u':.036308, 'd':.033844, 'p':.031671, 'm':.030129, 'h':.030034, 'g':.024705, 'b':.02720, 'f':.018121, 'y':.017779, 'w':.012899, 'k':.011016, 'v':.010074, 'x':.002902, 'z':.002722, 'j':.001965, 'q':.01962}

#Give each word in the dataframe a cumulative score
df['score'] = [sum(scores[word[pos]] for pos in range(5)) for word in wordList2]

df = df.sort_values(by='score', ascending=False)

###Do the default first guess
options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
OpenWordle.type_word('dream',driver)
OpenWordle.submit(driver)

#Loop fiv timesl
for guessNum in range(1,3):
    
    #Get the feedback
    known, unknown, removals = OpenWordle.read_row(guessNum, driver)
    [options.remove(letter) for letter in removals if letter is not None];
        
    #Narrow the search
    overlay = get_overlay(known, unknown, options, df)
    df = df[overlay]
    
    #Submit the most likely word
    
    OpenWordle.type_word(df.iloc[0,:5],driver)
    OpenWordle.submit(driver)
    






