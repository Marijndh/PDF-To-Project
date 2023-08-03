import datetime
import re
import ssl
from os import system, path
from sys import exit
from time import sleep
import certifi
import geopy.geocoders
import pytz
import requests
import win32com.client
from geopy.geocoders import Nominatim
from nltk import word_tokenize
from pdfminer.high_level import extract_text
import json

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
        print('Er is iets fout gegaan \n We proberen het opnieuw')
        ChooseAndSetPDF()


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
        sleep(5)
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


def SetData():
    global json_insertvalues
    global c
    referentie = ''
    projectnaam = ''
    straat = ''
    huisnummer = ''
    woonplaats = ''
    postcode = ''
    telefoon = ''
    email = ''
    contact = ''
    medewerkers = ''
    omschrijving = ''
    if c == 'BW':
        for w in range(len(w_list)):
            if w_list[w] == 'Opdrachtnummer' and referentie == '':
                referentie = w_list[w + 2]
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                for z in range(len(w_list) - w):
                    if w_list[w + z].isnumeric() and straat == '' and huisnummer == '':
                        straat = ' '.join(w_list[w + 4:w + z])
                        huisnummer = w_list[w + z]
                    if re.search(r"\b\d{4}\b", w_list[w + z]) and re.search(r"\b[A-Z]{2}\b", w_list[
                        w + z + 1]) and woonplaats == '' and postcode == '':
                        woonplaats = w_list[w + z + 2]
                        postcode = w_list[w + z] + ' ' + w_list[w + z + 1]
                        break
            if w_list[w][0] == '0' and w_list[w][1] == '6' and telefoon == '':
                if len(w_list[w]) >= 10:
                    telefoon = w_list[w]
                else:
                    for x in range(9):
                        if w_list[w + x].isnumeric():
                            telefoon += w_list[w + x]
            if w_list[w] == '@' and email == '':
                email = w_list[w - 1] + w_list[w] + w_list[w + 1]
            if w_list[w] == 'omschrijving' and w_list[w + 1] == ':' and omschrijving == '':
                dots = []
                omsc = ' '.join(w_list[w + 2:])
                for l in range(len(omsc)):
                    if omsc[l] == '.':
                        dots.append(l)
                for d in range(len(dots)):
                    if len(dots) == 1:
                        omschrijving += omsc[:dots[d] - 1] + omsc[dots[d]]
                    elif d == 0:
                        omschrijving += omsc[:dots[d] - 1] + omsc[dots[d]:dots[d + 1] - 1]
                    elif d != len(dots) - 1:
                        omschrijving += omsc[dots[d]:dots[d + 1] - 1]
                    else:
                        omschrijving += omsc[dots[d]]
        projectnaam = 'BW ' + straat + ' ' + huisnummer + ' ' + woonplaats
        contact = 2227585
        medewerkers = [{'id': 128345, 'firstName': 'Dennis', 'lastName': 'den Hollander',
                        'avatarFileHash': '240ef36c-88e9-4429-8dce-10acd636ba70'},
                       {'id': 128434, 'firstName': 'Olof', 'lastName': 'Eriks',
                        'avatarFileHash': '84b8feca-dc03-473f-a506-941399db5ec0'},
                       {'id': 128453, 'firstName': 'Tieme', 'lastName': 'Borst',
                        'avatarFileHash': '21da4364-1d28-4f0b-a75c-6a02b013bd67'}]

    elif c == 'WSAP':
        geolocator = Nominatim(user_agent="geoapiExercises")
        for w in range(len(w_list)):
            if w_list[w] == '/' and w_list[w + 2] == '/' and referentie == '':
                referentie = w_list[w - 1] + ' ' + w_list[w] + ' ' + w_list[w + 1] + ' ' + w_list[w + 2] + ' ' + w_list[
                    w + 3]
            if w_list[w] == 'Object' and w_list[w + 1] == ':' and huisnummer == '':
                for z in range(len(w_list)):
                    if w_list[w + 2 + z] == ',' and woonplaats == '':
                        woonplaats = w_list[w + 3 + z]
                    if w_list[w + z].isnumeric():
                        huisnummer = w_list[w + z]
                        straat = ' '.join(w_list[w + 2:w + z])
                        if straat != '' and postcode == '':
                            loc = geolocator.geocode(straat + " " + huisnummer)
                            postcode = geolocator.reverse(loc.point).raw['address']['postcode']
                            if woonplaats == '':
                                woonplaats = geolocator.reverse(loc.point).raw['address']['town']
                            break

            if w_list[w] == 'Telefoonnummer' and w_list[w + 1] == ':' and telefoon == '':
                for x in range(len(w_list) - w - 2):
                    if w_list[w + 2 + x] == ':' and w_list[w + 3 + x] == '06':
                        telefoon = ''.join(w_list[w + 3 + x:w + 2 + x + 6])
                        break
            if w_list[w] == 'Opdracht' and w_list[w + 1] == ':' and omschrijving == '':
                for x in range(len(w_list) - w):
                    if w_list[w + 2 + x] == 'Datum':
                        break
                    omschrijving += w_list[w + 2 + x]
                    if w_list[w + 3 + x] != '.':
                        omschrijving += ' '
        projectnaam = 'WSAP ' + straat + ' ' + huisnummer + ' ' + woonplaats
        contact = 2228633
        medewerkers = [{'id': 128345, 'firstName': 'Dennis', 'lastName': 'den Hollander',
                        'avatarFileHash': '240ef36c-88e9-4429-8dce-10acd636ba70'},
                       {'id': 128445, 'firstName': 'Chris', 'lastName': 'Stoop',
                        'avatarFileHash': '20b41093-4179-4621-924f-72b3d337ae18'},
                       {'id': 129808, 'firstName': 'Paul', 'lastName': 'Sinnige',
                        'avatarFileHash': 'bab77c4b-e5e4-4e6b-bd8a-7db32c196ff2'}]

    json_insertvalues = {
        "type": 0,
        "division": {
            "id": 2007,
            "salesInvoiceNumberPrefix": "01"
        },
        "name": projectnaam,
        "streetName": straat,
        "houseNumber": huisnummer,
        "zipCode": postcode,
        "city": woonplaats,
        "countryCode": "NL",
        "information": omschrijving,
        "branch": {
            "id": 3608,
            "division": {
                "id": 2007,
                "salesInvoiceNumberPrefix": "01"
            }
        },
        "contact": {
            "id": contact,
            "contactType": {
                "id": 0
            }
        },
        "category": {
            "id": 32514
        },
        "employees": medewerkers,
        "status": {
            "id": 55605
        },
        "customAttributeValues": [
            {
                "customAttribute": {
                    "id": 12679,
                },
                "value": telefoon
            },
            {
                "customAttribute": {
                    "id": 12680,
                },
                "value": email
            }
        ],
        "reference": referentie,
        "workAddress": straat + " " + huisnummer + ', ' + woonplaats,
        "projectLeader": {
            'id': 128345,
            'firstName': 'Dennis',
            'lastName': 'den Hollander',
            'avatarFileHash': '240ef36c-88e9-4429-8dce-10acd636ba70'
        }
    }


def GetToken():
    global token
    YOUR_APPLICATION_NAME = "pdf-to-project"
    YOUR_API_KEY = "eb6454df-9c2c9427-437d-9ad9-fc9c3094aa90"

    url = f"https://heimdall.bouw7.nl/auth/login/{YOUR_APPLICATION_NAME}/apiKey"

    headers = {
        "Accept": "application/json"
    }

    data = {
        "apiKey": YOUR_API_KEY
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        json_data = response.json()
        token = json_data['token']
        file = open('token.txt', 'w')
        file.write(json_data['exp'] + ': \n' + token)

    else:
        # Fout bij het aanvragen
        print(f"Fout bij aanvragen. Statuscode: {response.status_code}")
        print(response.text)


def TokenIsActive():
    file = open('token.txt', 'r')
    exp_date = file.readline()[:25]
    if exp_date == '':
        return False, ''
    file_token = file.readline()
    file.close()
    utc = pytz.UTC
    now = utc.localize(datetime.datetime.now())
    expired = datetime.datetime.strptime(exp_date, '%Y-%m-%dT%H:%M:%S%z')

    if now < expired:
        return True, file_token
    else:
        open('token.txt', 'w').close()
        return False, ''


def CreateProject():
    global token
    global json_insertvalues
    token_is_active, file_token = TokenIsActive()

    if token_is_active:
        token = file_token

    else:
        GetToken()

    url = "https://heimdall.bouw7.nl/project"

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }

    data = json.dumps(json_insertvalues)

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        json_data = response.text
        print(json_data)
    else:
        # Fout bij het aanvragen
        print(f"Fout bij aanvragen. Statuscode: {response.status_code}")
        print(response.text)


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
    global json_insertvalues
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
            file.write(json.dumps(json_insertvalues) + '\n')
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
    system('cls')
    FindEmail(None)
    w_list = FilterData()
    c = GetClient()
    SetData()
    CreateProject()
    EverythingWhentWell()


token = ''
results = []
c = ''
json_insertvalues = []
w_list = []

Main()
