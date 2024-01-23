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
            bw(window, w_list, json_values)
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


def bw(window, w_list, json_values):
    window.searching_for('Data filteren')
    for w in range(len(w_list)):
        if w_list[w] == 'Opdrachtnummer' and json_values["reference"] == '':
            json_values["reference"] = w_list[w + 2]
        if w_list[w] == 'Opdrachtbon':
            for z in range(len(w_list) - w - 1):
                if re.search(r"\b\d{4}\b", w_list[w + z]) and re.search(r"^[A-Z]{2}$", w_list[w + z + 1]) and \
                        json_values["city"] == '' and json_values["zipCode"] == '':
                    json_values["zipCode"] = w_list[w + z] + ' ' + w_list[w + z + 1]
                    json_values["city"] = w_list[w + z + 2]
                    json_values["houseNumber"] = w_list[w + z - 2]
                    json_values["streetName"] = w_list[w + z - 3]
        if w_list[w][0:2] == '06' or (
                w_list[w][0:4] == '0227' and json_values["customAttributeValues"][0]["value"] == ''):
            if sum(c.isdigit() for c in w_list[w]) == 10:
                json_values["customAttributeValues"][0]["value"] = w_list[w]
            else:
                number = w_list[w]
                for x in range(9):
                    if w_list[w + x].isnumeric() and w + x < len(w_list) - 1:
                        number += w_list[w + x]
                if sum(c.isdigit() for c in number) == 10:
                    json_values["customAttributeValues"][0]["value"] = number
        if w_list[w] == '@' and json_values["customAttributeValues"][1]["value"] == '':
            json_values["customAttributeValues"][1]["value"] = w_list[w - 1] + w_list[w] + w_list[w + 1]
        if w_list[w] == 'omschrijving' and w_list[w + 1] == ':' and json_values["information"] == '':
            description = ''
            for y in range(len(w_list) - w - 3):
                if w_list[w + y + 3].lower() == 'werksoortcode':
                    description = ' '.join(w_list[w + 3:w + y + 3])
                    break
            if description == '':
                description = ' '.join(w_list[w + 2:])
            description = description.replace(" ,", ",")
            description = description.replace(" .", ".")
            json_values["information"] = description
    json_values["name"] = 'BW ' + json_values["streetName"] + ' ' + json_values[
        "houseNumber"] + ' ' + json_values["city"]
    json_values["contact"]["id"] = 2227585
    json_values["employees"] = [{'id': 128434, 'firstName': 'Olof', 'lastName': 'Eriks',
                                 'avatarFileHash': '84b8feca-dc03-473f-a506-941399db5ec0'}]


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
    json_values["employees"] = [{'id': 128445, 'firstName': 'Chris', 'lastName': 'Stoop',
                                 'avatarFileHash': '20b41093-4179-4621-924f-72b3d337ae18'},
                                {'id': 129808, 'firstName': 'Paul', 'lastName': 'Sinnige',
                                 'avatarFileHash': 'bab77c4b-e5e4-4e6b-bd8a-7db32c196ff2'}]
    window.add_status_label("JSON File succesvol ingevuld met data")
