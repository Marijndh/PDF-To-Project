import os

from selenium import webdriver
from selenium.webdriver.common.by import By
import win32com.client
import pyautogui
import pyperclip
from pdfminer.high_level import extract_text


# Find email based on input
# https://towardsdatascience.com/automatic-download-email-attachment-with-python-4aa59bc66c25
def FindEmail(titel):
    message = None
    result = None
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)
    messages = inbox.Items
    for msg in messages:
        if msg.subject.lower() == titel.lower():
            message = msg
            break
    if message is None:
        os.system('cls')
        print("Email niet gevonden")
        titel = input("Wat is de titel van de email?: ")
        FindEmail(titel)
    else:
        print("Gevonden")
        for attachment in message.Attachments:
            if str(attachment)[-3:] == 'pdf':
                result = attachment
                break
        result.SaveAsFile(os.path.join(__file__[0:-7], 'file.pdf'))


def GetTitel():
    hm = pyHook.HookManager()
    hm.MouseAll = uMad
    hm.KeyAll = uMad
    hm.HookMouse()
    hm.HookKeyboard()
    pythoncom.PumpMessages()
    first = pyautogui.position()
    loc = pyautogui.locateCenterOnScreen("leftOftitel.png")
    if loc is None:
        print("Open eerst outlook voordat het programma werkt, of geef de titel door")
        return ''
    pyautogui.moveTo(loc.x + 20, loc.y - 2)
    pyautogui.moveTo(loc.x + 1200, loc.y - 2)
    pyautogui.dragTo(loc.x, loc.y)
    pyautogui.hotkey('ctrl', 'c')
    title = pyperclip.paste()
    pyautogui.leftClick()
    pyautogui.moveTo(first)
    return title


def InsertData(data):
    # open website
    driver = webdriver.Chrome()
    driver.get("https://www.google.com")

    # send data to html elements
    driver.find_element(By.ID, "L2AGLb").click()
    element = driver.find_element(By.ID, "APjFqb")
    element.send_keys("Hallo")


def FilterData():
    _pdf = "file.pdf"
    _dataRows = extract_text(_pdf)
    print(_dataRows)


os.system('cls')
FilterData()
