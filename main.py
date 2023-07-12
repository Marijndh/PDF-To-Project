import xmlrpc.client
from os import system, path
from time import sleep
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import win32com.client
import pyautogui
from pyperclip import paste
from pdfminer.high_level import extract_text
from nltk import word_tokenize
import pandas as pd
import certifi
import ssl
import geopy.geocoders
from geopy.geocoders import Nominatim

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx


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
        system('cls')
        print("Email niet gevonden")
        titel = input("Wat is de titel van de email?: ")
        FindEmail(titel)
    else:
        print("Gevonden")
        for attachment in message.Attachments:
            if str(attachment)[-3:] == 'pdf':
                result = attachment
                break
        result.SaveAsFile(path.join(__file__[0:-7], 'file.pdf'))


def GetTitel():
    first = pyautogui.position()
    loc = pyautogui.locateCenterOnScreen("leftOftitel.png")
    if loc is None:
        print("Open eerst outlook voordat het programma werkt, of geef de titel door")
        return ''
    pyautogui.moveTo(loc.x + 20, loc.y - 2)
    pyautogui.moveTo(loc.x + 1200, loc.y - 2)
    pyautogui.dragTo(loc.x, loc.y)
    pyautogui.hotkey('ctrl', 'c')
    title = paste()
    pyautogui.leftClick()
    pyautogui.moveTo(first)
    return title


def FilterData():
    _pdf = "file.pdf"
    try:
        _dataRows = extract_text(_pdf)
    except:
        x = 10
        print("PDF bestand is niet mogelijk om te openen\nProbeer het opnieuw\nAan het afsluiten...")
        while x > 0:
            x -= 1
            if x != 0:
                print(str(x), end='')
                sleep(0.2)
                print('.', end='')
                sleep(0.2)
                print('.', end='')
                sleep(0.2)
                print('.', end='')
                sleep(0.4)
            else:
                print('0')
                sleep(1)
        exit()

    return word_tokenize(_dataRows)


def ClientNotFound():
    c_input = input("Opdrachtgever kan niet gevonden worden, wie is de opdrachtgever?\nBW of WSAP?: ")
    c_input_upper = c_input.upper()

    if c_input_upper != "BW" and c_input_upper != "WSAP":
        print(c_input_upper)
        system("cls")
        print("Verkeerde input")
        ClientNotFound()
    else:
        return c_input_upper


def GetClient():
    for word in w_list:
        if word.lower() == 'opdrachtbon':
            return 'BW'
        if word.lower() == 'werkopdracht':
            return 'WSAP'
    return ClientNotFound()


class InputValue:
    def __init__(self, name, inputId, value, type):
        self.name = name
        self.id = inputId
        self.value = value
        self.type = type


def CreateInputValues():
    df = pd.read_excel('Data.xlsx', sheet_name='Main')
    values = df.values.tolist()
    input_instances = []
    for v in values:
        input_instances.append(InputValue(*v))
    return input_instances


class FillSwitch:
    def getValue(self, name):
        default = "Incorrect name"
        return getattr(self, str(c) + "_" + str(name), lambda: default)()

    def BW_Referentie(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Opdrachtnummer':
                return w_list[w + 2]
        return None

    def BW_Projectnaam(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                return 'Test: BW ' + w_list[w + 4] + ' ' + w_list[w + 5] + ' ' + w_list[w + 9]
        return None

    def BW_Postcode(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                return w_list[w + 7] + ' ' + w_list[w + 8]
        return None

    def BW_Huisnummer(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                return w_list[w + 5]
        return None

    def BW_Straat(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                return w_list[w + 4]
        return None

    def BW_Plaats(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                return w_list[w + 9]
        return None

    def BW_Telefoon(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                return w_list[w + 18]
        return None

    def BW_Email(self):
        for w in range(len(w_list)):
            if w_list[w] == '@':
                return w_list[w - 1] + w_list[w] + w_list[w + 1]
        return None

    def BW_Contact(self):
        return "Woningbouwvereniging Beter Wonen"

    def BW_Medewerkers(self):
        return ["Dennis den Hollander", "Olof Eriks", "Tieme Borst"]

    def BW_Omschrijving(self):
        dots = []
        om = ''
        for w in range(len(w_list)):
            if w_list[w] == 'omschrijving' and w_list[w + 1] == ':':
                omschrijving = ' '.join(w_list[w + 2:])
                for l in range(len(omschrijving)):
                    if omschrijving[l] == '.':
                        dots.append(l)
                for d in range(len(dots)):
                    if len(dots) == 1:
                        om += omschrijving[:dots[d] - 1] + omschrijving[dots[d]]
                        continue
                    elif d == 0:
                        om += omschrijving[:dots[d] - 1] + omschrijving[dots[d]:dots[d + 1] - 1]
                    elif d != len(dots) - 1:
                        om += omschrijving[dots[d]:dots[d + 1] - 1]
                    else:
                        om += omschrijving[dots[d]]
                return om
        return None

    def WSAP_Referentie(self):
        for w in range(len(w_list)):
            if w_list[w] == '/' and w_list[w + 2] == '/':
                return w_list[w - 1] + ' ' + w_list[w] + ' ' + w_list[w + 1] + ' ' + w_list[w + 2] + ' ' + w_list[w + 3]
        return None

    def WSAP_Projectnaam(self):
        projectname = 'Test: WSAP '
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for x in range(len(w_list) - w):
                    if w_list[w + 2 + x] != ',':
                        projectname += w_list[w + 2 + x] + ' '
                    else:
                        projectname += w_list[w + 2 + x + 1]
                        break
                return projectname
        return None

    def WSAP_Postcode(self):
        geolocator = Nominatim(user_agent="geoapiExercises")
        adress = ''
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for x in range(len(w_list) - w):
                    if w_list[w + 2 + x] != ',':
                        adress += w_list[w + 2 + x] + ' '
                    else:
                        adress += w_list[w + 2 + x + 1]
                        break
                return ' '.join(geolocator.geocode(adress).raw['display_name'].split()[-3:-1])[:-1]
        return None

    def WSAP_Huisnummer(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for x in range(len(w_list) - w):
                    if w_list[w + x] == ',':
                        return w_list[w + x - 1]
        return None

    def WSAP_Straat(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for x in range(len(w_list) - w):
                    if w_list[w + 2 + x] == ',':
                        return ' '.join(w_list[w + 2: w + 1 + x])
        return None

    def WSAP_Plaats(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for x in range(len(w_list) - w):
                    if w_list[w + 2 + x] == ',':
                        return w_list[w + 3 + x]
        return None

    def WSAP_Telefoon(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Telefoonnummer' and w_list[w + 1] == ':':
                for x in range(len(w_list) - w):
                    if w_list[w + 2 + x] == ':' and w_list[w + 3 + x] == '06':
                        return ''.join(w_list[w + 3 + x:w + 2 + x + 6])
        return None

    def WSAP_Email(self):
        return None

    def WSAP_Contact(self):
        return 'Woningstichting Anna Paulowna'

    def WSAP_Medewerkers(self):
        return ["Dennis den Hollander", "Chris Stoop", "Paul Sinnige"]

    def WSAP_Omschrijving(self):
        opdracht = ''
        for w in range(len(w_list)):
            if w_list[w] == 'Opdracht' and w_list[w + 1] == ':':
                for x in range(len(w_list) - w):
                    if w_list[w + 2 + x] == 'Datum':
                        return opdracht
                    opdracht += w_list[w + 2 + x]
                    if w_list[w + 3 + x] != '.':
                        opdracht += ' '
        return None


def InsertDataIntoInputs():
    switch = FillSwitch()
    for x in inputvalue_list:
        if type(x.value) == float:
            x.value = switch.getValue(x.name)


def GetChildComponents(driver, id, value, xpath):
    _inputselect = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, id)))
    sleep(0.1)
    driver.execute_script("arguments[0].click();", _inputselect)
    ActionChains(driver) \
        .move_to_element(_inputselect) \
        .send_keys(value) \
        .perform()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, xpath)))
    answers = driver.find_elements(By.XPATH, xpath)
    return answers


def InsertData(driver):
    for inputitem in inputvalue_list:
        try:
            if inputitem.name == 'Omschrijving':
                _inputselect = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                                               '/html/body/div[1]/div/div[1]/div[2]/div/div/form[1]/div/div[2]/div/div[12]/div[2]/div[2]/div[2]/div/p')))
                ActionChains(driver).move_to_element(_inputselect)
                _inputselect.send_keys(inputitem.value[::-1])
                continue

            if inputitem.name == 'Medewerkers':
                answers = GetChildComponents(driver, inputitem.id, '',
                                             f"//div[@class='dropdown-item v-list-item v-list-item--link theme--light']")
                for x in range(len(inputitem.value)):
                    for answer in answers:
                        if answer.text.lower() == inputitem.value[x].lower():
                            answer.click()
                            break
                continue

            if inputitem.name == 'Contact':
                answers = GetChildComponents(driver, inputitem.id, inputitem.value,
                                             f"//div[@class='v-list-item__subtitle text-truncate filter-input-max']")
                answers[0].click()
                continue

            if inputitem.type == 'input':
                _input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, inputitem.id)))
                _input.send_keys(inputitem.value)
                continue

            if inputitem.type == 'select':
                answers = GetChildComponents(driver, inputitem.id, inputitem.value,
                                             f"//div[@class='v-list-item__title']")
                for answer in answers:
                    if answer.text.lower() == inputitem.value.lower():
                        answer.click()
                        break

        except Exception as e:
            print(str(e))
            print('\n' + inputitem.name)


def StartupDriver():
    options = Options()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    driver.set_window_position(0, -1200)
    driver.get("https://login.bouw7.nl/")
    try:
        mailinput = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "loginform-username")))
        mailinput.send_keys("dennis@bouwbedrijfhollandskroon.nl")
        button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/b7-app/main/div[3]/b7-frame/div[3]/form/div/button')))
        button.click()
        passwordinput = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[2]/div/div[2]/form/div[3]/div[2]/input')))
        passwordinput.send_keys('Wst256Wst256!')
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[2]/div[1]/div/div/div/div[2]/div/div[2]/form/div[3]/div[4]/button')))
        button.click()
        form = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/b7-app/main/div[3]/b7-frame/div[3]/div/b7-tenant/form')))
        form.click()
        button = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div/header/div[2]/a[2]')))
        button.click()
    except:
        driver.quit()
        print("Kan de juiste website elementen niet vinden om naar de website te gaan, probeer opnieuw")
    InsertData(driver)
    elementpos = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div/div[1]/h1")
    ActionChains(driver).move_to_element(elementpos).click(elementpos).perform()
    driver.set_window_position(0, 0)


system('cls')
inputvalue_list = CreateInputValues()
w_list = FilterData()
c = GetClient()
InsertDataIntoInputs()
StartupDriver()
