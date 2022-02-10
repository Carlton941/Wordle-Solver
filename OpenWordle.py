# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 21:03:38 2022

@author: Carlton
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pyautogui

def submit(driver):
    js = 'document.querySelector("body > game-app").shadowRoot.querySelector("#game > game-keyboard").shadowRoot.querySelector("#keyboard > div:nth-child(3) > button:nth-child(1)").click()'
    driver.execute_script(js)
    sleep(1)

def type_word(word, driver):
    for letter in word:
        js = 'return document.querySelector("body > game-app").shadowRoot.querySelector("#game > game-keyboard").shadowRoot.querySelector("#keyboard").querySelector("[data-key = \'' + letter + '\']")'
        key = driver.execute_script(js)
        key.click()
    sleep(1)

def read_row(rowNum, driver):
    unknown = {1:None, 2:None, 3:None, 4:None, 5:None}
    known = {1:None, 2:None, 3:None, 4:None, 5:None}
    removals = {1:None, 2:None, 3:None, 4:None, 5:None}
    for tileNum in range(1,6):
        js = 'return document.querySelector("body > game-app").shadowRoot.querySelector("#board > game-row:nth-child(' + str(rowNum) +')").shadowRoot.querySelector("div > game-tile:nth-child(' + str(tileNum) + ')")'
        gameTile = driver.execute_script(js)
        letter = gameTile.get_attribute('letter')
        evaluation = gameTile.get_attribute('evaluation')
        if evaluation == 'correct':
            known[tileNum] = letter
        elif evaluation == 'present':
            unknown[tileNum] = letter
        else:
            removals[tileNum] = letter
    sleep(1)
    success = all(x is not None for x in known.values())
    return known, unknown, removals, success

def open_page():
    #Get the webdriver
    driver = webdriver.Chrome(executable_path='C:\\Program Files\\Chrome Driver\\chromedriver.exe')
    
    #Open the wordle webpage
    driver.get('https://www.powerlanguage.co.uk/wordle/')
    driver.maximize_window()
    sleep(1)
    
    
    #Close the intro box on the webpage
    pyautogui.click(900,500)
    sleep(1)
    return driver
