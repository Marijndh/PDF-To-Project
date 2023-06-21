import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import win32com.client

os.system('cls')


# Find email based on input
# https://towardsdatascience.com/automatic-download-email-attachment-with-python-4aa59bc66c25
def VindEmail():
    input_subject = input("Wat is de titel van de email?:  ")

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)
    messages = inbox.Items
    for msg in messages:
        try:
            if msg.subject.lower() == input_subject.lower():
                message = msg
                break
            else:
                message = None
        except Exception:
            print(Exception)
    if message == None:
        os.system('cls')
        print("Email niet gevonden, probeer opnieuw")
        VindEmail()
    else:
        print("Gevonden")
        return message.Body


text = VindEmail()

# open website
driver = webdriver.Chrome()
driver.get("https://www.google.com")

# send data to html elements
driver.find_element(By.ID, "L2AGLb").click()
element = driver.find_element(By.ID, "APjFqb")
element.send_keys("Hallo")
