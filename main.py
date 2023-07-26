import datetime
import re
import ssl
from os import system, path
from time import sleep
from sys import exit

import certifi
import geopy.geocoders
import pandas as pd
import win32com.client
from geopy.geocoders import Nominatim
from nltk import word_tokenize
from pdfminer.high_level import extract_text
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx


def ChooseAndSetPDF():
    for x in range(len(results)):
        print(results[x].Filename + '  (' + str(x) + ')')
    getal = input()
    try:
        results[int(getal)].SaveAsFile(path.join(__file__[0:-7], 'file.pdf'))
        del results[int(getal)]
    except:
        system('cls')
        print('Verkeerd getal \n We proberen het opnieuw')


def ReadAttachments(message):
    global results
    for attachment in message.Attachments:
        if str(attachment)[-3:] == 'pdf':
            results.append(attachment)
    if len(results) == 1:
        results[0].SaveAsFile(path.join(__file__[0:-7], 'file.pdf'))
    elif len(results) > 1:
        system('cls')
        print('Welke pdf wil je uit laten lezen? \n Geef het getal wat achter de pdf staat')
        ChooseAndSetPDF()
    else:
        print("Geen pdf te vinden in deze mail \n we proberen het opnieuw")
        FindEmail(None)


def FindEmail(titel):
    message = None
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)
    messages = inbox.Items
    outlook = win32com.client.Dispatch("Outlook.Application")
    if outlook.ActiveExplorer() is not None:
        selection = outlook.ActiveExplorer().Selection
        if selection.Count > 0:
            message = selection.Item(1)
    if titel is not None:
        for msg in messages:
            if msg.subject.lower() == titel.lower():
                message = msg
                break
    if message is None:
        system('cls')
        titel = input("Wat is de titel van de email?: ")
        FindEmail(titel)
    else:
        ReadAttachments(message)


def FilterData():
    _pdf = "file.pdf"
    try:
        _dataRows = extract_text(_pdf)
    except:
        system('cls')
        print("PDF bestand is niet mogelijk om te openen\nProbeer het opnieuw\n")
        exit()

    return word_tokenize(_dataRows)


def ClientNotFound():
    system('cls')
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
        return ''

    def BW_Projectnaam(self):
        straat = ''
        huisnummer = ''
        woonplaats = ''
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                for z in range(len(w_list) - w):
                    if w_list[w + z].isnumeric() and straat == '':
                        straat = ' '.join(w_list[w + 4:w + z])
                        huisnummer = w_list[w + z]
                    if re.search(r"\b\d{4}\b", w_list[w + z]) and re.search(r"\b[A-Z]{2}\b", w_list[w + z + 1]):
                        woonplaats = w_list[w + z + 2]

        return 'BW ' + straat + ' ' + huisnummer + ' ' + woonplaats

    def BW_Postcode(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                for z in range(len(w_list) - w):
                    if re.search(r"\b\d{4}\b", w_list[w + z]) and re.search(r"\b[A-Z]{2}\b", w_list[w + z + 1]):
                        return w_list[w + z] + ' ' + w_list[w + z + 1]
        return ''

    def BW_Huisnummer(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                for z in range(len(w_list)):
                    if w_list[w + z].isnumeric():
                        return w_list[w + z]
        return ''

    def BW_Straat(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                for z in range(0, w + 2):
                    if w_list[w + z].isnumeric():
                        return ' '.join(w_list[w + 4:w + z])
        return ''

    def BW_Plaats(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                for z in range(len(w_list) - w):
                    if re.search(r"\b\d{4}\b", w_list[w + z]) and re.search(r"\b[A-Z]{2}\b", w_list[w + z + 1]):
                        return w_list[w + z + 2]
        return ''

    def BW_Telefoon(self):
        number = ''
        for w in range(len(w_list)):
            if w_list[w][0] == '0' and w_list[w][1] == '6':
                if len(w_list[w]) >= 10:
                    return w_list[w]
                else:
                    for x in range(9):
                        if w_list[w + x].isnumeric():
                            number += w_list[w + x]
                        else:
                            return number
        return ''

    def BW_Email(self):
        for w in range(len(w_list)):
            if w_list[w] == '@':
                return w_list[w - 1] + w_list[w] + w_list[w + 1]
        return ''

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
        return ''

    def WSAP_Referentie(self):
        for w in range(len(w_list)):
            if w_list[w] == '/' and w_list[w + 2] == '/':
                return w_list[w - 1] + ' ' + w_list[w] + ' ' + w_list[w + 1] + ' ' + w_list[w + 2] + ' ' + w_list[w + 3]
        return ''

    def WSAP_Projectnaam(self):
        straat = ''
        woonplaats = ''
        geolocator = Nominatim(user_agent="geoapiExercises")
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for z in range(len(w_list)):
                    if w_list[w + z].isnumeric():
                        straat = ' '.join(w_list[w + 2:w + z + 1])
                        break
        try:
            loc = geolocator.geocode(straat)
            woonplaats = geolocator.reverse(loc.point).raw['address']['town']
        except:
            print('')

        return 'WSAP ' + straat + ' ' + woonplaats

    def WSAP_Postcode(self):
        geolocator = Nominatim(user_agent="geoapiExercises")
        adress = ''
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for z in range(len(w_list)):
                    if w_list[w + z].isnumeric():
                        adress = ' '.join(w_list[w + 2:w + z + 1])
                        break
        try:
            loc = geolocator.geocode(adress)
            return geolocator.reverse(loc.point).raw['address']['postcode']
        except:
            return ''

    def WSAP_Huisnummer(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for z in range(len(w_list)):
                    if w_list[w + z].isnumeric():
                        return w_list[w + z]
        return ''

    def WSAP_Straat(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for z in range(len(w_list)):
                    if w_list[w + z].isnumeric():
                        return ' '.join(w_list[w + 2:w + z])
        return ''

    def WSAP_Plaats(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for x in range(len(w_list) - w - 2):
                    if w_list[w + 2 + x] == ',':
                        return w_list[w + 3 + x]
        geolocator = Nominatim(user_agent="geoapiExercises")
        adress = ''
        for w in range(len(w_list)):
            if w_list[w] == 'Object' and w_list[w + 1] == ':':
                for z in range(len(w_list)):
                    if w_list[w + z].isnumeric():
                        adress = ' '.join(w_list[w + 2:w + z + 1])
                        break
        try:
            loc = geolocator.geocode(adress)
            return geolocator.reverse(loc.point).raw['address']['town']
        except:
            return ''

    def WSAP_Telefoon(self):
        for w in range(len(w_list)):
            if w_list[w] == 'Telefoonnummer' and w_list[w + 1] == ':':
                for x in range(len(w_list) - w - 2):
                    if w_list[w + 2 + x] == ':' and w_list[w + 3 + x] == '06':
                        return ''.join(w_list[w + 3 + x:w + 2 + x + 6])
        return ''

    def WSAP_Email(self):
        for w in range(len(w_list)):
            if w_list[w] == '@':
                return w_list[w - 1] + w_list[w] + w_list[w + 1]
        return ''

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
        return ''


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
            print('Error bij het invullen van: ' + inputitem.name)


def StartupDriver():
    options = Options()
    options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager(version="114.0.5735.90").install())
    driver = webdriver.Chrome(options=options, service=service)
    driver.maximize_window()
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
        exit()
    InsertData(driver)
    elementpos = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div[1]/div/div[1]/h1")
    ActionChains(driver).move_to_element(elementpos).click(elementpos).perform()


def Again():
    global c
    global w_list
    global inputvalue_list
    system('cls')
    if len(results) > 0:
        again = input('Wil je nog een pdf laten invoeren uit dezelfde mail?: (Y/N) \n')
        if again.upper() == 'Y':
            ChooseAndSetPDF()
    again = input('Wil je nog een pdf laten invoeren uit een nieuwe mail?: (Y/N) \n')
    if again.upper() == 'Y':
        print('Druk op enter als de volgende mail klaar staat')
        input('')
        sleep(1)
        Main()
    if again.upper() == 'N':
        exit()
    else:
        system('cls')
        print('Verkeerde input, voer Y of N in als YES of NO')
        Again()


def EverythingWhentWell():
    system('cls')
    i = input('Is alles goed gegaan?: (Y/N) \n')
    if i.upper() == 'Y':
        Again()
    if i.upper() == 'N':
        file = open('log.txt', 'w')
        data = input('Wat is er precies fout gegaan?: \n')
        if data != '':
            time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            file.write(time + ': ' + data + '\n')
            for x in inputvalue_list:
                if type(x.value) is list:
                    file.write('[' + x.name + ': ')
                    for y in range(len(x.value)):
                        file.write(x.value[y] + ' ')
                    file.write('] ')
                else:
                    file.write('[' + x.name + ': ' + str(x.value) + '] ')
            file.write('\n\n')
            Again()
        else:
            print('Er is wat fout gegaan, we proberen het opnieuw')
            EverythingWhentWell()
    else:
        system('cls')
        print('Verkeerde input, voer Y of N in als YES of NO')
        EverythingWhentWell()


def Main():
    global c
    global w_list
    global inputvalue_list
    system('cls')
    FindEmail(None)
    inputvalue_list = CreateInputValues()
    w_list = FilterData()
    c = GetClient()
    InsertDataIntoInputs()
    StartupDriver()
    EverythingWhentWell()


results = []
inputvalue_list = ''
w_list = ''
c = ''
Main()
