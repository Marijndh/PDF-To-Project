import json
import re
import ssl

import certifi
import geopy
from geopy.geocoders import Nominatim

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx


def filter_data(client, log_file, window, w_list, json_values):
    if not json_values:
        with open('data.json') as f:
            json_values = json.load(f)
    try:
        if client == 'BW':
            bw(client, window, w_list, json_values)
        elif client == 'WSAP':
            wsap(window, w_list, json_values)
    except Exception as e:
        if str(e) == 'Non-successful status code 403':
            json_values["zipCode"] = ' '
            log_file.write('Fout bij opzoeken van postcode: ' + str(e) + '\n')
            window.add_status_label('Postcode kon niet gevonden worden')
            wsap(window, w_list, json_values)
        else:
            window.add_status_label('Fout bij het ophalen van de data uit deze mail')
            log_file.write('Fout bij het ophalen van de data: ' + str(e) + '\n' + json.dumps(json_values) + '\n')
    return json_values


def bw(client, window, w_list, json_values):
    window.searching_for('Data filteren')
    if client == 'BW' and w_list != []:
        for w in range(len(w_list)):
            if w_list[w] == 'Opdrachtnummer' and json_values["reference"] == '':
                json_values["reference"] = w_list[w + 2]
            if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':
                for z in range(len(w_list) - w):
                    if w_list[w + z].isnumeric() and json_values["streetName"] == '' and json_values[
                        "houseNumber"] == '':
                        json_values["streetName"] = ' '.join(w_list[w + 4:w + z])
                        json_values["houseNumber"] = w_list[w + z]
                    if re.search(r"\b\d{4}\b", w_list[w + z]) and json_values["city"] == '' and \
                            json_values[
                                "zipCode"] == '' and w + z < len(w_list) - 1:
                        if re.search(r"\b[A-Z]{2}\b", w_list[w + z + 1]):
                            json_values["city"] = w_list[w + z + 2]
                            json_values["zipCode"] = w_list[w + z] + ' ' + w_list[w + z + 1]
                            break
            if w_list[w][0:1] == '06' and json_values["customAttributeValues"][0]["value"] == '' or w_list[w][
                                                                                                    0:3] == '0227':
                if len(w_list[w]) >= 10:
                    json_values["customAttributeValues"][0]["value"] = w_list[w]
                else:
                    for x in range(9):
                        if w_list[w + x].isnumeric() and w + x < len(w_list) - 1:
                            json_values["customAttributeValues"][0]["value"] += w_list[w + x]
            if w_list[w] == '@' and json_values["customAttributeValues"][1]["value"] == '':
                json_values["customAttributeValues"][1]["value"] = w_list[w - 1] + w_list[w] + w_list[w + 1]
            if w_list[w] == 'omschrijving' and w_list[w + 1] == ':' and json_values["information"] == '':
                dots = []
                description = ' '.join(w_list[w + 2:])
                for l in range(len(description)):
                    if description[l] == '.':
                        dots.append(l)
                if not dots:
                    json_values["information"] = description
                    break
                for d in range(len(dots)):
                    if len(dots) == 1:
                        json_values["information"] += description[:dots[d] - 1] + description[dots[d]]
                    elif d == 0:
                        json_values["information"] += description[:dots[d] - 1] + description[dots[d]:dots[d + 1] - 1]
                    elif d != len(dots) - 1:
                        json_values["information"] += description[dots[d]:dots[d + 1] - 1]
                    else:
                        json_values["information"] += description[dots[d]]
        json_values["name"] = 'BW ' + json_values["streetName"] + ' ' + json_values[
            "houseNumber"] + ' ' + json_values["city"]
        json_values["contact"]["id"] = 2227585
        json_values["employees"] = [{'id': 128345, 'firstName': 'Dennis', 'lastName': 'den Hollander',
                                     'avatarFileHash': '240ef36c-88e9-4429-8dce-10acd636ba70'},
                                    {'id': 128434, 'firstName': 'Olof', 'lastName': 'Eriks',
                                     'avatarFileHash': '84b8feca-dc03-473f-a506-941399db5ec0'},
                                    {'id': 128453, 'firstName': 'Tieme', 'lastName': 'Borst',
                                     'avatarFileHash': '21da4364-1d28-4f0b-a75c-6a02b013bd67'}]


def wsap(window, w_list, json_values):
    locator = Nominatim(user_agent="geoapiExercises")
    for w in range(len(w_list)):
        if w_list[w] == '/' and w_list[w + 2] == '/' and json_values["reference"] == '':
            json_values["reference"] = w_list[w - 1] + ' ' + w_list[w] + ' ' + w_list[w + 1] + ' ' + \
                                       w_list[w + 2] + ' ' + \
                                       w_list[
                                           w + 3]
        if w_list[w] == 'Object' and w_list[w + 1] == ':' and json_values["houseNumber"] == '':
            for z in range(len(w_list)):
                if w_list[w + 2 + z] == ',' and json_values["city"] == '' and w + z + 2 < len(w_list) - 1:
                    json_values["city"] = w_list[w + 3 + z]
                if w_list[w + z].isnumeric() and json_values["streetName"] == '':
                    json_values["houseNumber"] = w_list[w + z]
                    json_values["streetName"] = ' '.join(w_list[w + 2:w + z])
                    if json_values["streetName"] != '' and json_values["zipCode"] == '':
                        loc = locator.geocode(
                            json_values["streetName"] + " " + json_values["houseNumber"])
                        zip_code = locator.reverse(loc.point).raw['address'][
                            'postcode']
                        json_values["zipCode"] = zip_code
                        if json_values["city"] == '':
                            json_values["city"] = locator.reverse(loc.point).raw['address']['town']
                        break

        if w_list[w] == 'Telefoonnummer' and w_list[w + 1] == ':' and \
                json_values["customAttributeValues"][0]["value"] == '':
            for x in range(len(w_list) - w - 2):
                if w_list[w + 2 + x] == ':' and w_list[w + 3 + x] == '06' or w_list[w + 3 + x] == '0227':
                    json_values["customAttributeValues"][0]["value"] = ''.join(
                        w_list[w + 3 + x:w + 2 + x + 6])
                    break
        if w_list[w] == 'Opdracht' and w_list[w + 1] == ':' and json_values["information"] == '':
            for x in range(len(w_list) - w):
                if w_list[w + 2 + x] == 'Datum':
                    break
                json_values["information"] += w_list[w + 2 + x]
                if w_list[w + 3 + x] != '.':
                    json_values["information"] += ' '
    json_values["name"] = 'WSAP ' + json_values["streetName"] + ' ' + json_values[
        "houseNumber"] + ' ' + json_values["city"]
    json_values["contact"]["id"] = 2228633
    json_values["employees"] = [{'id': 128345, 'firstName': 'Dennis', 'lastName': 'den Hollander',
                                 'avatarFileHash': '240ef36c-88e9-4429-8dce-10acd636ba70'},
                                {'id': 128445, 'firstName': 'Chris', 'lastName': 'Stoop',
                                 'avatarFileHash': '20b41093-4179-4621-924f-72b3d337ae18'},
                                {'id': 129808, 'firstName': 'Paul', 'lastName': 'Sinnige',
                                 'avatarFileHash': 'bab77c4b-e5e4-4e6b-bd8a-7db32c196ff2'}]
    window.add_status_label("JSON File succesvol ingevuld met data")
