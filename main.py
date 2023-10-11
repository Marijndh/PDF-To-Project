import datetimeimport jsonimport osimport reimport sslimport sysimport threadingfrom os import pathfrom time import sleepimport certifiimport geopy.geocodersimport nltkimport requestsimport win32com.clientfrom PyQt5.QtWidgets import QApplicationfrom geopy.geocoders import Nominatimfrom nltk import word_tokenizefrom pdfminer.high_level import extract_textimport GUInltk.download('punkt')ctx = ssl.create_default_context(cafile=certifi.where())geopy.geocoders.options.default_ssl_context = ctxdef ChooseAndSetPDF():    window.Searching_For('PDF ophalen')    global log_file    global results    q = 'Welke pdf wil je uit laten lezen? \n Geef het getal wat achter de pdf staat \n'    for x in range(len(results)):        q += results[x].Filename + '  (' + str(x) + ')\n'    getal = window.AskQuestion(q)    try:        getal = int(getal)        if getal < len(results):            SaveFile(getal, None)        else:            raise Exception()    except:        window.Alert('Vul een geldig getal in, we proberen het opnieuw')        ChooseAndSetPDF()def SaveFile(getal, message):    global results    try:        window.Searching_For('Bijlage opslaan')        results[int(getal)].SaveAsFile(os.getcwd() + "\\file.pdf")        while not os.path.exists("file.pdf"):            sleep(1)        log_file.write('PDF geselecteerd: ' + results[0].Filename + '\n')        window.AddStatusLabel('PDF geselecteerd: ' + results[0].Filename)        del results[int(getal)]    except Exception as e:        log_file.write('Fout bij het opslaan van de pdf: ' + str(e) + '\n')        window.Alert('Fout bij het opslaan van de pdf: ' + str(e))        if message is None:            ChooseAndSetPDF()        else:            ReadAttachments(message)def ReadAttachments(message):    window.Searching_For('Bijlagen uitlezen')    global log_file    global results    if len(results) > 1:        ChooseAndSetPDF()    elif len(results) == 1:        SaveFile(0, message)    else:        for attachment in message.Attachments:            if str(attachment)[-3:] == 'pdf':                results.append(attachment)        if len(results) == 0:            window.Alert("Deze mail bevat geen pdf's")            FindEmail()        else:            ReadAttachments(message)def FindEmail():    window.Searching_For('Mail zoeken')    global log_file    try:        outlook = win32com.client.Dispatch("Outlook.Application")        if outlook.ActiveExplorer() is not None:            selection = outlook.ActiveExplorer().Selection            if selection.Count > 0:                message = selection.Item(1)                log_file.write('Email gevonden: ' + message.subject + '\n')                window.AddStatusLabel('Email gevonden: ' + message.subject)                window.SetTitel(message.subject)                ReadAttachments(message)        else:            window.Alert("Kan de geselecteerde email niet vinden, klik op de juiste email")            FindEmail()    except Exception as e:        log_file.write('Fout bij het vinden van de geselecteerde email: ' + str(e) + '\n')        FindEmail()def FilterData():    window.Searching_For('Data uit pdf lezen')    global log_file    global w_list    try:        if os.path.exists("file.pdf"):            _pdf = "file.pdf"            _dataRows = extract_text(_pdf)            window.AddStatusLabel('Data is succesvol uit de pdf gehaald')            log_file.write('Data is uit de pdf gehaald: \n' + _dataRows + '\n')            w_list = word_tokenize(_dataRows)        else:            log_file.write('Fout bij het openen van de pdf: \n')            window.Alert("PDF bestand is niet mogelijk om te openen\nWe proberen het opnieuw\n")            FindEmail()    except Exception as e:        log_file.write(f'Fout bij het openen van de pdf: {e} \n')        print("PDF bestand is niet mogelijk om te openen\nWe proberen het opnieuw\n")        FindEmail()def ClientNotFound():    global log_file    window.Searching_For('Zoeken naar client')    c_input_upper = window.AskQuestion(        "Opdrachtgever kan niet gevonden worden, wie is de opdrachtgever?\nBW of WSAP?: ")    if c_input_upper != "BW" and c_input_upper != "WSAP":        window.Alert('Geen correcte input, we proberen het opnieuw')        ClientNotFound()    else:        window.AddStatusLabel('Client gevonden: ' + c_input_upper)        log_file.write('Client gevonden: ' + c_input_upper + '\n')        return c_input_upperdef GetClient():    global client    window.Searching_For('Client ophalen uit mail')    for word in w_list:        if word.lower() == 'opdrachtbon':            log_file.write('Client gevonden: BW\n')            window.AddStatusLabel('Client gevonden: BW')            client = 'BW'        elif word.lower() == 'werkopdracht':            client = 'WSAP'            log_file.write('Client gevonden: WSAP\n')            window.AddStatusLabel('Client gevonden: WSAP')    if client == '':        ClientNotFound()# noinspection PyTypeCheckerdef SetData():    window.Searching_For('Data filteren')    global log_file    global json_insertvalues    global client    try:        with open('data.json') as f:            if not json_insertvalues:                json_insertvalues = json.load(f)        if client == 'BW' and w_list != []:            for w in range(len(w_list)):                if w_list[w] == 'Opdrachtnummer' and json_insertvalues["reference"] == '':                    json_insertvalues["reference"] = w_list[w + 2]                if w_list[w] == 'Gereed' and w_list[w + 1] == 'voor':                    for z in range(len(w_list) - w):                        if w_list[w + z].isnumeric() and json_insertvalues["streetName"] == '' and json_insertvalues[                            "houseNumber"] == '':                            json_insertvalues["streetName"] = ' '.join(w_list[w + 4:w + z])                            json_insertvalues["houseNumber"] = w_list[w + z]                        if re.search(r"\b\d{4}\b", w_list[w + z]) and json_insertvalues["city"] == '' and \                                json_insertvalues[                                    "zipCode"] == '' and w + z < len(w_list) - 1:                            if re.search(r"\b[A-Z]{2}\b", w_list[w + z + 1]):                                json_insertvalues["city"] = w_list[w + z + 2]                                json_insertvalues["zipCode"] = w_list[w + z] + ' ' + w_list[w + z + 1]                                break                if w_list[w][0:1] == '06' and json_insertvalues["customAttributeValues"][0][                    "value"] == '' or w_list[w][0:3] == '0227':                    if len(w_list[w]) >= 10:                        json_insertvalues["customAttributeValues"][0]["value"] = w_list[w]                    else:                        for x in range(9):                            if w_list[w + x].isnumeric() and w + x < len(w_list) - 1:                                json_insertvalues["customAttributeValues"][0]["value"] += w_list[w + x]                if w_list[w] == '@' and json_insertvalues["customAttributeValues"][1]["value"] == '':                    json_insertvalues["customAttributeValues"][1]["value"] = w_list[w - 1] + w_list[w] + w_list[w + 1]                if w_list[w] == 'omschrijving' and w_list[w + 1] == ':' and json_insertvalues["information"]:                    dots = []                    omsc = ' '.join(w_list[w + 2:])                    for l in range(len(omsc)):                        if omsc[l] == '.':                            dots.append(l)                    if not dots:                        json_insertvalues["information"] = omsc                        break                    for d in range(len(dots)):                        if len(dots) == 1:                            json_insertvalues["information"] += omsc[:dots[d] - 1] + omsc[dots[d]]                        elif d == 0:                            json_insertvalues["information"] += omsc[:dots[d] - 1] + omsc[dots[d]:dots[d + 1] - 1]                        elif d != len(dots) - 1:                            json_insertvalues["information"] += omsc[dots[d]:dots[d + 1] - 1]                        else:                            json_insertvalues["information"] += omsc[dots[d]]            json_insertvalues["name"] = 'BW ' + json_insertvalues["streetName"] + ' ' + json_insertvalues[                "houseNumber"] + ' ' + json_insertvalues["city"]            json_insertvalues["contact"]["id"] = 2227585            json_insertvalues["employees"] = [{'id': 128345, 'firstName': 'Dennis', 'lastName': 'den Hollander',                                               'avatarFileHash': '240ef36c-88e9-4429-8dce-10acd636ba70'},                                              {'id': 128434, 'firstName': 'Olof', 'lastName': 'Eriks',                                               'avatarFileHash': '84b8feca-dc03-473f-a506-941399db5ec0'},                                              {'id': 128453, 'firstName': 'Tieme', 'lastName': 'Borst',                                               'avatarFileHash': '21da4364-1d28-4f0b-a75c-6a02b013bd67'}]        elif client == 'WSAP' and w_list != []:            geolocator = Nominatim(user_agent="geoapiExercises")            for w in range(len(w_list)):                if w_list[w] == '/' and w_list[w + 2] == '/' and json_insertvalues["reference"] == '':                    json_insertvalues["reference"] = w_list[w - 1] + ' ' + w_list[w] + ' ' + w_list[w + 1] + ' ' + \                                                     w_list[w + 2] + ' ' + \                                                     w_list[                                                         w + 3]                if w_list[w] == 'Object' and w_list[w + 1] == ':' and json_insertvalues["houseNumber"] == '':                    for z in range(len(w_list)):                        if w_list[w + 2 + z] == ',' and json_insertvalues["city"] == '' and w + z + 2 < len(w_list) - 1:                            json_insertvalues["city"] = w_list[w + 3 + z]                        if w_list[w + z].isnumeric() and json_insertvalues["streetName"] == '':                            json_insertvalues["houseNumber"] = w_list[w + z]                            json_insertvalues["streetName"] = ' '.join(w_list[w + 2:w + z])                            if json_insertvalues["streetName"] != '' and json_insertvalues["zipCode"] == '':                                loc = geolocator.geocode(                                    json_insertvalues["streetName"] + " " + json_insertvalues["houseNumber"])                                zipCode = geolocator.reverse(loc.point).raw['address'][                                    'postcode']                                json_insertvalues["zipCode"] = zipCode                                if json_insertvalues["city"] == '':                                    json_insertvalues["city"] = geolocator.reverse(loc.point).raw['address']['town']                                break                if w_list[w] == 'Telefoonnummer' and w_list[w + 1] == ':' and \                        json_insertvalues["customAttributeValues"][0]["value"] == '':                    for x in range(len(w_list) - w - 2):                        if w_list[w + 2 + x] == ':' and w_list[w + 3 + x] == '06' or w_list[w + 3 + x] == '0227':                            json_insertvalues["customAttributeValues"][0]["value"] = ''.join(                                w_list[w + 3 + x:w + 2 + x + 6])                            break                if w_list[w] == 'Opdracht' and w_list[w + 1] == ':' and json_insertvalues["information"] == '':                    for x in range(len(w_list) - w):                        if w_list[w + 2 + x] == 'Datum':                            break                        json_insertvalues["information"] += w_list[w + 2 + x]                        if w_list[w + 3 + x] != '.':                            json_insertvalues["information"] += ' '            json_insertvalues["name"] = 'WSAP ' + json_insertvalues["streetName"] + ' ' + json_insertvalues[                "houseNumber"] + ' ' + json_insertvalues["city"]            json_insertvalues["contact"]["id"] = 2228633            json_insertvalues["employees"] = [{'id': 128345, 'firstName': 'Dennis', 'lastName': 'den Hollander',                                               'avatarFileHash': '240ef36c-88e9-4429-8dce-10acd636ba70'},                                              {'id': 128445, 'firstName': 'Chris', 'lastName': 'Stoop',                                               'avatarFileHash': '20b41093-4179-4621-924f-72b3d337ae18'},                                              {'id': 129808, 'firstName': 'Paul', 'lastName': 'Sinnige',                                               'avatarFileHash': 'bab77c4b-e5e4-4e6b-bd8a-7db32c196ff2'}]        window.AddStatusLabel("JSON File succesvol ingevuld met data")    except Exception as e:        if str(e) == 'Non-successful status code 403':            json_insertvalues["zipCode"] = ''            log_file.write('Fout bij opzoeken van postcode: ' + str(e) + '\n')            window.AddStatusLabel('Postcode kon niet gevonden worden')            SetData()        else:            window.AddStatusLabel('Fout bij het ophalen van de data uit deze mail')            log_file.write('Fout bij het ophalen van de data: ' + str(e) + '\n' + json.dumps(json_insertvalues) + '\n')def GetToken():    window.Searching_For('Token ophalen')    global log_file    try:        YOUR_APPLICATION_NAME = "pdf-to-project"        YOUR_API_KEY = "eb6454df-9c2c9427-437d-9ad9-fc9c3094aa90"        url = f"https://heimdall.bouw7.nl/auth/login/{YOUR_APPLICATION_NAME}/apiKey"        headers = {            "Accept": "application/json"        }        data = {            "apiKey": YOUR_API_KEY        }        response = requests.post(url, headers=headers, data=data)        if response.status_code == 200:            window.AddStatusLabel('Nieuwe token is succesvol opgehaald')            log_file.write('Nieuwe token opgehaald\n')            json_data = response.json()            filename = 'options.json'            with open(filename, 'r') as f:                token_file = json.load(f)                token_file["token"] = json_data['token']            os.remove(filename)            with open(filename, 'w') as f:                json.dump(token_file, f, indent=4)            CreateProject()        else:            GetToken()    except Exception as e:        log_file.write('Fout bij het ophalen van een nieuwe token: ' + str(e) + '\n')def CreateProject():    window.Searching_For('Project aanmaken')    global log_file    global json_insertvalues    try:        with open('options.json') as f:            token_file = json.load(f)            token = token_file["token"]        url = "https://heimdall.bouw7.nl/project"        headers = {            'Accept': 'application/json',            'Content-Type': 'application/json',            'Authorization': 'Bearer ' + token        }        data = json.dumps(json_insertvalues)        response = requests.post(url, headers=headers, data=data)        if response.status_code == 201:            window.Searching_For('Project is toegevoegd')            window.AddStatusLabel("Project is succesvol toegevoegd")            log_file.write('Gestuurde JSON: ' + json.dumps(json_insertvalues) + '\n')        elif response.status_code == 400:            window.AddStatusLabel("Mislukt om dit project toe te voegen")            log_file.write(f"Fout bij aanvragen. Statuscode: {response.status_code}, Text: {response.text}\n")        elif response.status_code == 403:            log_file.write(f"Fout bij aanvragen. Statuscode: {response.status_code}, Text: {response.text}\n")            GetToken()    except Exception as e:        log_file.write('Fout bij het sturen van het project: ' + str(e) + '\n')        CreateProject()def Again():    global results    if len(results) > 0:        again = window.AskQuestion('Wil je nog een pdf laten invoeren uit dezelfde mail?: (Y/N) \n')        if again.upper() == 'Y':            Main()        elif again.upper() == 'N':            results = []        else:            Again()def SendMail(file_path):    try:        if log_file.closed:            outlook = win32com.client.Dispatch('outlook.application')            mail = outlook.CreateItem(0)            mail.To = 'pdftoprojectreceipts@gmail.com'            mail.Subject = 'Log-File'            if os.path.exists('file.pdf'):                mail.Attachments.Add(os.getcwd() + "\\file.pdf")            with open(file_path, 'r') as f:                mail.Body = f.read()            mail.Send()            window.AddStatusLabel("Email verstuurd")        else:            log_file.close()            SendMail(file_path)    except Exception as e:        with open(file_path, 'w') as file:            file.write('Mislukt om email te sturen: ' + str(e))        window.AddStatusLabel("Mislukt om email te sturen")def EverythingWhentWell():    global log_file    window.Searching_For(' ')    i = window.AskQuestion('Is alles goed gegaan?: (Y/N) \n')    if i.upper() == 'Y':        Again()    elif i.upper() == 'N':        data = window.AskQuestion('Wat is er precies fout gegaan?: \n')        if data is not None and data != '':            log_file.write('Opmerking: ' + data + '\n')            SendMail(log_file.name)            Again()        else:            window.Alert('Er is wat fout gegaan, we proberen het opnieuw')            EverythingWhentWell()    else:        EverythingWhentWell()def Main():    global log_file    window.SetRunningMain(True)    window.ClearFoundObject()    window.AddLogs()    log_file = open(f'Logs/{datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S")}.txt', 'w')    FindEmail()    FilterData()    log_file.write('Woordenlijst: ' + w_list.__str__() + '\n')    GetClient()    SetData()    CreateProject()    EverythingWhentWell()    if os.path.exists("file.pdf"):        os.remove("file.pdf")    if not log_file.closed:        log_file.close()    window.AddLogs()    window.SetRunningMain(False)def FindTitleLoop():    while not window.running_main:        try:            outlook = win32com.client.Dispatch("Outlook.Application")            selection = outlook.ActiveExplorer().Selection            if selection.Count > 0:                message = selection.Item(1)                window.SetTitel(message.subject)            if window.run_main_again:                window.run_main_again = False                Main()            if window.send_email != '':                SendMail('Logs/' + window.send_email)                window.send_email = ''        except:            window.SetTitel("*Nog geen email titel kunnen vinden*")ctx = ssl.create_default_context(cafile=certifi.where())geopy.geocoders.options.default_ssl_context = ctxlog_file = ''results = []client = ''json_insertvalues = []w_list = []if os.path.exists("file.pdf"):    os.remove("file.pdf")app = QApplication(sys.argv)window = GUI.MainWindow()thread_1 = threading.Thread(target=window.show())thread_2 = threading.Thread(target=Main())thread_3 = threading.Thread(target=FindTitleLoop())thread_1.start()thread_2.start()thread_3.start()app.exec()