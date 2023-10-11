import json
import os
import re
import ssl
from time import sleep

import certifi
import geopy.geocoders
import nltk
import win32com.client
from geopy.geocoders import Nominatim
from nltk import word_tokenize
from pdfminer.high_level import extract_text

nltk.download('punkt')
ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx


def SaveFile():
    global result
    result.SaveAsFile(os.getcwd() + "\\file.pdf")
    while not os.path.exists("file.pdf"):
        sleep(1)


def ReadAttachments(message):
    global result
    for attachment in message.Attachments:
        if str(attachment)[-3:] == 'pdf':
            result = attachment


def FindEmail():
    outlook = win32com.client.Dispatch("Outlook.Application")
    if outlook.ActiveExplorer() is not None:
        selection = outlook.ActiveExplorer().Selection
        if selection.Count > 0:
            message = selection.Item(1)
            ReadAttachments(message)
            SaveFile()


def FilterData():
    global w_list
    if os.path.exists("file.pdf"):
        _pdf = "file.pdf"
        _dataRows = extract_text(_pdf)
        w_list = word_tokenize(_dataRows)


def GetClient():
    global client
    for word in w_list:
        if word.lower() == 'opdrachtbon':
            client = 'BW'
        if word.lower() == 'werkopdracht':
            client = 'WSAP'
    if client == '':
        print("Geen client kunnen vinden")


# noinspection PyTypeChecker
def SetData():
    global json_insertvalues
    global client
    with open('data.json') as f:
        if not json_insertvalues:
            json_insertvalues = json.load(f)
    if client == 'BW' and w_list != []:
        for w in range(len(w_list)):
            if w_list[w] == 'Opdrachtnummer' and json_insertvalues["reference"] == '':
                json_insertvalues["reference"] = w_list[w + 2]
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                for z in range(len(w_list) - w):
                    if w_list[w + z].isnumeric() and json_insertvalues["streetName"] == '' and json_insertvalues[
                        "houseNumber"] == '':
                        json_insertvalues["streetName"] = ' '.join(w_list[w + 4:w + z])
                        json_insertvalues["houseNumber"] = w_list[w + z]
                    if re.search(r"\b\d{4}\b", w_list[w + z]) and json_insertvalues["city"] == '' and json_insertvalues[
                        "zipCode"] == '' and w + z < len(w_list) - 1:
                        if re.search(r"\b[A-Z]{2}\b", w_list[w + z + 1]):
                            json_insertvalues["city"] = w_list[w + z + 2]
                            json_insertvalues["zipCode"] = w_list[w + z] + ' ' + w_list[w + z + 1]
                            break
            if w_list[w][0:1] == '06' and json_insertvalues["customAttributeValues"][0][
                "value"] == '' or w_list[w][0:3] == '0227':
                if len(w_list[w]) >= 10:
                    json_insertvalues["customAttributeValues"][0]["value"] = w_list[w]
                else:
                    for x in range(9):
                        if w_list[w + x].isnumeric() and w + x < len(w_list) - 1:
                            json_insertvalues["customAttributeValues"][0]["value"] += w_list[w + x]
            if w_list[w] == '@' and json_insertvalues["customAttributeValues"][1]["value"] == '':
                json_insertvalues["customAttributeValues"][1]["value"] = w_list[w - 1] + w_list[w] + w_list[w + 1]
            if w_list[w] == 'omschrijving' and w_list[w + 1] == ':' and json_insertvalues["information"]:
                dots = []
                omsc = ' '.join(w_list[w + 2:])
                for l in range(len(omsc)):
                    if omsc[l] == '.':
                        dots.append(l)
                if not dots:
                    json_insertvalues["information"] = omsc
                    break
                for d in range(len(dots)):
                    if len(dots) == 1:
                        json_insertvalues["information"] += omsc[:dots[d] - 1] + omsc[dots[d]]
                    elif d == 0:
                        json_insertvalues["information"] += omsc[:dots[d] - 1] + omsc[dots[d]:dots[d + 1] - 1]
                    elif d != len(dots) - 1:
                        json_insertvalues["information"] += omsc[dots[d]:dots[d + 1] - 1]
                    else:
                        json_insertvalues["information"] += omsc[dots[d]]
        json_insertvalues["name"] = 'BW ' + json_insertvalues["streetName"] + ' ' + json_insertvalues[
            "houseNumber"] + ' ' + json_insertvalues["city"]
        json_insertvalues["contact"]["id"] = 2227585
        json_insertvalues["employees"] = [{'id': 128345, 'firstName': 'Dennis', 'lastName': 'den Hollander',
                                           'avatarFileHash': '240ef36c-88e9-4429-8dce-10acd636ba70'},
                                          {'id': 128434, 'firstName': 'Olof', 'lastName': 'Eriks',
                                           'avatarFileHash': '84b8feca-dc03-473f-a506-941399db5ec0'},
                                          {'id': 128453, 'firstName': 'Tieme', 'lastName': 'Borst',
                                           'avatarFileHash': '21da4364-1d28-4f0b-a75c-6a02b013bd67'}]

    elif client == 'WSAP' and w_list != []:
        geolocator = Nominatim(user_agent="geoapiExercises")
        for w in range(len(w_list)):
            if w_list[w] == '/' and w_list[w + 2] == '/' and json_insertvalues["reference"] == '':
                json_insertvalues["reference"] = w_list[w - 1] + ' ' + w_list[w] + ' ' + w_list[w + 1] + ' ' + \
                                                 w_list[w + 2] + ' ' + \
                                                 w_list[
                                                     w + 3]
            if w_list[w] == 'Object' and w_list[w + 1] == ':' and json_insertvalues["houseNumber"] == '':
                for z in range(len(w_list)):
                    if w_list[w + 2 + z] == ',' and json_insertvalues["city"] == '' and w + z + 2 < len(w_list) - 1:
                        json_insertvalues["city"] = w_list[w + 3 + z]
                    if w_list[w + z].isnumeric() and json_insertvalues["streetName"] == '':
                        json_insertvalues["houseNumber"] = w_list[w + z]
                        json_insertvalues["streetName"] = ' '.join(w_list[w + 2:w + z])
                        if json_insertvalues["streetName"] != '' and json_insertvalues["zipCode"] == '':
                            loc = geolocator.geocode(
                                json_insertvalues["streetName"] + " " + json_insertvalues["houseNumber"])
                            zipCode = geolocator.reverse(loc.point).raw['address'][
                                'postcode']
                            json_insertvalues["zipCode"] = zipCode
                            if json_insertvalues["city"] == '':
                                json_insertvalues["city"] = geolocator.reverse(loc.point).raw['address']['town']
                            break

            if w_list[w] == 'Telefoonnummer' and w_list[w + 1] == ':' and \
                    json_insertvalues["customAttributeValues"][0]["value"] == '':
                for x in range(len(w_list) - w - 2):
                    if w_list[w + 2 + x] == ':' and w_list[w + 3 + x] == '06' or w_list[w + 3 + x] == '0227':
                        json_insertvalues["customAttributeValues"][0]["value"] = ''.join(
                            w_list[w + 3 + x:w + 2 + x + 6])
                        break
            if w_list[w] == 'Opdracht' and w_list[w + 1] == ':' and json_insertvalues["information"] == '':
                for x in range(len(w_list) - w):
                    if w_list[w + 2 + x] == 'Datum':
                        break
                    json_insertvalues["information"] += w_list[w + 2 + x]
                    if w_list[w + 3 + x] != '.':
                        json_insertvalues["information"] += ' '
        json_insertvalues["name"] = 'WSAP ' + json_insertvalues["streetName"] + ' ' + json_insertvalues[
            "houseNumber"] + ' ' + json_insertvalues["city"]
        json_insertvalues["contact"]["id"] = 2228633
        json_insertvalues["employees"] = [{'id': 128345, 'firstName': 'Dennis', 'lastName': 'den Hollander',
                                           'avatarFileHash': '240ef36c-88e9-4429-8dce-10acd636ba70'},
                                          {'id': 128445, 'firstName': 'Chris', 'lastName': 'Stoop',
                                           'avatarFileHash': '20b41093-4179-4621-924f-72b3d337ae18'},
                                          {'id': 129808, 'firstName': 'Paul', 'lastName': 'Sinnige',
                                           'avatarFileHash': 'bab77c4b-e5e4-4e6b-bd8a-7db32c196ff2'}]


client = ''
w_list = []
result = None
json_insertvalues = []


def Main():
    FindEmail()
    FilterData()
    GetClient()
    SetData()
    print(w_list)
    print(json_insertvalues)

    if os.path.exists("file.pdf"):
        os.remove("file.pdf")


Main()
