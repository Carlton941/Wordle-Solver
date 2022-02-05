# -*- coding: utf-8 -*-
"""
Created on Fri Feb  4 20:09:37 2022

@author: Carlton
"""
import os
import pandas as pd
from functools import reduce

os.chdir('C://Users//Carlton//Documents//Wordle')

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

#Letters that might be in the word
options = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

#Letters that are somewhere in the word
unknown = {1:None, 2:None, 3:None, 4:None, 5:None}

#Definite letters
known = {1:None, 2:None, 3:None, 4:None, 5:None}

#For first two initial guesses, default to 'dream' and 'hoist'
#Then get the results from the user
optionsResults = input('Enter the letters that are not in the word.\n')
unknownResults = input('Enter the unknown letters with underscores to indicate blanks.\n')
knownResults = input('Enter the known letters with underscores to indicate blanks.\n')

for i in range(3):
    #Update the options, unknown and known trackers
    [options.remove(letter) for letter in optionsResults if letter in options];
    [(unknown.update({index+1:unknownResults[index]})) for index in range(5) if unknownResults[index] != '_'];
    [(known.update({index+1:knownResults[index]})) for index in range(5) if knownResults[index] != '_'];
    
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
    df = df[overlay]
    
    #Return the top three choices from the remaining words, based on their cumulative scores
    print('\n',df.head(3))
    
    #Get the user's input on the latest result
    optionsResults = input('Enter the letters that are not in the word.\n')
    unknownResults = input('Enter the letters that appear in an unknown location in the word.\n')
    knownResults = input('Enter the known letters with underscores to indicate blanks.\n')






