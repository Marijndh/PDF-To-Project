import json
import re
import ssl
import certifi
import geopy
from geopy.geocoders import Nominatim

# SSL setup for Geopy
ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx

# Constants
DEFAULT_CONTACTS = {
    "BW": {"id": 2227585, "employees": [{'id': 128434, 'firstName': 'Olof', 'lastName': 'Eriks',
                                         'avatarFileHash': '84b8feca-dc03-473f-a506-941399db5ec0'}]},
    "WSAP": {"id": 2228633, "employees": [{'id': 128445, 'firstName': 'Chris', 'lastName': 'Stoop',
                                           'avatarFileHash': '20b41093-4179-4621-924f-72b3d337ae18'},
                                          {'id': 129808, 'firstName': 'Paul', 'lastName': 'Sinnige',
                                           'avatarFileHash': 'bab77c4b-e5e4-4e6b-bd8a-7db32c196ff2'}]}
}


# Utility functions
def load_default_json(file_path="project-template.json"):
    """Load default JSON data from a file."""
    with open(file_path) as f:
        return json.load(f)


def extract_information(pattern, data, default=""):
    """Extract information from data using a regex pattern."""
    match = re.search(pattern, data)
    return match.group(0) if match else default


def update_address(locator, project):
    """Update missing zip code and city based on street name and house number."""
    if project["streetName"] and not project["zipCode"]:
        loc = locator.geocode(f'{project["streetName"]} {project["houseNumber"]}')
        if loc:
            address = locator.reverse(loc.point).raw['address']
            project["zipCode"] = address.get('postcode', '')
            project["city"] = project["city"] or address.get('town', '')


def handle_exception(e, project, log_file, window, fallback_function, *args):
    """Handle exceptions and attempt recovery."""
    if str(e) == 'Non-successful status code 403':
        project["zipCode"] = ' '
        log_file.write(f'Error finding zip code: {e}\n')
        window.add_status_label('Postcode kon niet gevonden worden')
        fallback_function(*args)
    else:
        log_file.write(f'Error processing data: {e}\n{json.dumps(project)}\n')
        window.add_status_label('Error retrieving data from this mail')


# Core logic
def filter_data(client, log_file, window, words, project=None):
    """Filter data based on client and populate project."""
    project = project or load_default_json()
    locator = Nominatim(user_agent="geoapiExercises")

    client_function = bw if client == 'BW' else wsap if client == 'WSAP' else None
    if client_function:
        try:
            client_function(window, words, project, locator)
        except Exception as e:
            handle_exception(e, project, log_file, window, client_function, words)
    else:
        window.add_status_label(f"Unknown client: {client}")
    return project


def bw(window, words, project, locator):
    """Process data for BW client."""
    window.searching_for('Data filteren')
    for w, word in enumerate(words):
        if word == 'Opdrachtnummer' and not project["reference"]:
            project["reference"] = words[w + 2]
        elif word == 'Opdrachtbon':
            extract_opdrachtbon_data(w, words, project)
        elif word[:2] == '06' or (word[:4] == '0227' and not project["customAttributeValues"][0]["value"]):
            extract_phone_number(w, words, project)
        elif word == '@' and not project["customAttributeValues"][1]["value"]:
            project["customAttributeValues"][1]["value"] = words[w - 1] + word + words[w + 1]
        elif word == 'omschrijving' and words[w + 1] == ':' and not project["information"]:
            project["information"] = extract_description(w, words)

    project["name"] = f'BW {project["streetName"]} {project["houseNumber"]} {project["city"]}'
    project.update(DEFAULT_CONTACTS["BW"])


def wsap(window, words, project, locator):
    """Process data for WSAP client."""
    for w, word in enumerate(words):
        if word == '/' and words[w + 2] == '/' and not project["reference"]:
            project["reference"] = f'{words[w - 1]} {word} {words[w + 1]} {words[w + 2]} {words[w + 3]}'
        elif word == 'Object' and words[w + 1] == ':' and not project["houseNumber"]:
            extract_object_data(w, words, project)
        elif word == 'Telefoonnummer' and words[w + 1] == ':' and not project["customAttributeValues"][0]["value"]:
            extract_telephone_data(w, words, project)
        elif word == 'Opdracht' and words[w + 1] == ':' and not project["information"]:
            project["information"] = extract_information_list(w + 2, words, 'Datum')

    update_address(locator, project)
    project["name"] = f'WSAP {project["streetName"]} {project["houseNumber"]} {project["city"]}'
    project.update(DEFAULT_CONTACTS["WSAP"])
    window.add_status_label("JSON File successfully updated with data")


# Helper extraction functions
def extract_opdrachtbon_data(w, words, project):
    for z in range(len(words) - w - 1):
        if re.search(r"\b\d{4}\b", words[w + z]) and re.search(r"^[A-Z]{2}$", words[w + z + 1]) and \
                not project["city"] and not project["zipCode"]:
            project["zipCode"] = f'{words[w + z]} {words[w + z + 1]}'
            project["city"] = words[w + z + 2]
            project["houseNumber"] = words[w + z - 2]
            project["streetName"] = words[w + z - 3]


def extract_phone_number(w, words, project):
    number = words[w]
    for x in range(9):
        if words[w + x].isnumeric() and w + x < len(words) - 1:
            number += words[w + x]
    if sum(c.isdigit() for c in number) == 10:
        project["customAttributeValues"][0]["value"] = number


def extract_description(w, words):
    description = []
    for y in range(3, len(words) - w - 3):
        if words[w + y].lower() == 'werksoortcode':
            return ' '.join(words[w:w + y]).replace(" ,", ",").replace(" .", ".")
    return ' '.join(words[w + 2:]).replace(" ,", ",").replace(" .", ".")


def extract_object_data(w, words, project):
    for z in range(3, len(words) - w - 1):
        if words[w + z] == ',' and not project["city"]:
            project["city"] = ' '.join(words[w + z + 1:])
        elif words[w + z].isnumeric() and not project["streetName"]:
            project["houseNumber"] = words[w + z]
            project["streetName"] = ' '.join(words[w + 2:w + z])


def extract_telephone_data(w, words, project):
    for x in range(len(words) - w - 1):
        if words[w + x][:2] == '06' or words[w + x][:3] == '022':
            project["customAttributeValues"][0]["value"] = words[w + x]
            break


def extract_information_list(start, words, stop_word):
    return ' '.join(word for word in words[start:] if word != stop_word)
