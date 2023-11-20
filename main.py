import datetimeimport jsonimport osimport sslimport sysimport threadingfrom time import sleepimport certifiimport geopy.geocodersimport nltkimport requestsimport win32com.clientfrom PyQt5.QtWidgets import QApplicationfrom nltk import word_tokenizefrom pdfminer.high_level import extract_textfrom PIL import Imagefrom pdf2image import convert_from_pathimport pytesseractimport data_filterimport guinltk.download('punkt')def choose_and_set_pdf():    window.searching_for('PDF ophalen')    global results    q = 'Welke pdf wil je uit laten lezen? \n Geef het getal wat achter de pdf staat \n'    for x in range(len(results)):        q += results[x].Filename + '  (' + str(x) + ')\n'    getal = window.ask_question(q)    try:        getal = int(getal)        if getal < len(results):            save_file(getal, None)        else:            raise Exception()    except Exception as e:        window.alert('Vul een geldig getal in, we proberen het opnieuw')        log_file.write('Fout bij het kiezen van een pdf: ' + str(e) + '\n')        choose_and_set_pdf()def save_file(getal, message):    global results    try:        window.searching_for('Bijlage opslaan')        results[int(getal)].SaveAsFile(os.getcwd() + "\\file.pdf")        while not os.path.exists("file.pdf"):            sleep(1)        log_file.write('PDF geselecteerd: ' + results[0].Filename + '\n')        window.add_status_label('PDF geselecteerd: ' + results[0].Filename)        del results[int(getal)]    except Exception as e:        log_file.write('Fout bij het opslaan van de pdf: ' + str(e) + '\n')        window.alert('Fout bij het opslaan van de pdf: ' + str(e))        if message is None:            choose_and_set_pdf()        else:            read_attachments(message)def read_attachments(message):    window.searching_for('Bijlagen uitlezen')    global results    if len(results) > 1:        choose_and_set_pdf()    elif len(results) == 1:        save_file(0, message)    else:        for attachment in message.Attachments:            if str(attachment)[-3:] == 'pdf':                results.append(attachment)        if len(results) == 0:            window.alert("Deze mail bevat geen pdf's")            find_email()        else:            read_attachments(message)def find_email():    window.searching_for('Mail zoeken')    try:        outlook = win32com.client.Dispatch("Outlook.Application")        if outlook.ActiveExplorer() is not None:            selection = outlook.ActiveExplorer().Selection            if selection.Count > 0:                message = selection.Item(1)                log_file.write('Email gevonden: ' + message.subject + '\n')                window.add_status_label('Email gevonden: ' + message.subject)                window.set_titel(message.subject)                read_attachments(message)        else:            window.alert("Kan de geselecteerde email niet vinden, klik op de juiste email")            find_email()    except Exception as e:        log_file.write('Fout bij het vinden van de geselecteerde email: ' + str(e) + '\n')        find_email()def filter_data():    window.searching_for('Data uit pdf lezen')    global w_list    try:        if os.path.exists("file.pdf"):            _pdf = "file.pdf"            _dataRows = extract_text(_pdf)            w_list = word_tokenize(_dataRows)            if not w_list:                pdf_images = convert_from_path('file.pdf', poppler_path='poppler-23.11.0/Library/bin')                pdf_images[0].save('image.png', 'PNG')                pytesseract.pytesseract.tesseract_cmd = r'Tesseract/tesseract.exe'                w_list = str(pytesseract.image_to_string(Image.open('image.png')))            window.add_status_label('Data is succesvol uit de pdf gehaald')            log_file.write('Data is uit de pdf gehaald: \n' + _dataRows + '\n')        else:            log_file.write('Fout bij het openen van de pdf: \n')            window.alert("PDF bestand is niet mogelijk om te openen\nWe proberen het opnieuw\n")            find_email()    except Exception as e:        log_file.write(f'Fout bij het openen van de pdf: {e} \n')        find_email()def client_not_found():    window.searching_for('Zoeken naar client')    c_input_upper = window.ask_question(        "Opdrachtgever kan niet gevonden worden, wie is de opdrachtgever?\nBW of WSAP?: ")    if c_input_upper != "BW" and c_input_upper != "WSAP":        window.alert('Geen correcte input, we proberen het opnieuw')        client_not_found()    else:        window.add_status_label('Client gevonden: ' + c_input_upper)        log_file.write('Client gevonden: ' + c_input_upper + '\n')        return c_input_upperdef get_client():    global client    window.searching_for('Client ophalen uit mail')    for word in w_list:        if word.lower() == 'opdrachtbon':            log_file.write('Client gevonden: BW\n')            window.add_status_label('Client gevonden: BW')            client = 'BW'        elif word.lower() == 'werkopdracht':            client = 'WSAP'            log_file.write('Client gevonden: WSAP\n')            window.add_status_label('Client gevonden: WSAP')    if client == '':        client_not_found()def get_token():    window.searching_for('Token ophalen')    try:        your_application_name = "pdf-to-project"        your_api_key = "eb6454df-9c2c9427-437d-9ad9-fc9c3094aa90"        url = f"https://heimdall.bouw7.nl/auth/login/{your_application_name}/apiKey"        headers = {            "Accept": "application/json"        }        data = {            "apiKey": your_api_key        }        response = requests.post(url, headers=headers, data=data)        if response.status_code == 200:            window.add_status_label('Nieuwe token is succesvol opgehaald')            log_file.write('Nieuwe token opgehaald\n')            json_data = response.json()            filename = 'options.json'            with open(filename, 'r') as f:                token_file = json.load(f)                token_file["token"] = json_data['token']            os.remove(filename)            with open(filename, 'w') as f:                json.dump(token_file, f, indent=4)            create_project()        else:            get_token()    except Exception as e:        log_file.write('Fout bij het ophalen van een nieuwe token: ' + str(e) + '\n')def create_project():    window.searching_for('Project aanmaken')    try:        with open('options.json') as f:            token_file = json.load(f)            token = token_file["token"]        url = "https://heimdall.bouw7.nl/project"        headers = {            'Accept': 'application/json',            'Content-Type': 'application/json',            'Authorization': 'Bearer ' + token        }        data = json.dumps(json_values)        response = requests.post(url, headers=headers, data=data)        if response.status_code == 201:            window.searching_for('Project is toegevoegd')            window.add_status_label("Project is succesvol toegevoegd")            log_file.write('Gestuurde JSON: ' + json.dumps(json_values) + '\n')        elif response.status_code == 400:            window.add_status_label("Mislukt om dit project toe te voegen")            log_file.write(f"Fout bij aanvragen. Statuscode: {response.status_code}, Text: {response.text}\n")        elif response.status_code == 403:            log_file.write(f"Fout bij aanvragen. Statuscode: {response.status_code}, Text: {response.text}\n")            get_token()    except Exception as e:        log_file.write('Fout bij het sturen van het project: ' + str(e) + '\n')        create_project()def again():    global results    if len(results) > 0:        redo = window.ask_question('Wil je nog een pdf laten invoeren uit dezelfde mail?: (Y/N) \n')        if redo.upper() == 'Y':            main()        elif redo.upper() == 'N':            results = []        else:            redo()def send_mail(file_path):    try:        if log_file.closed:            outlook = win32com.client.Dispatch('outlook.application')            mail = outlook.CreateItem(0)            mail.To = 'pdftoprojectreceipts@gmail.com'            mail.Subject = 'Log-File'            if os.path.exists('file.pdf'):                mail.Attachments.Add(os.getcwd() + "\\file.pdf")            with open(file_path, 'r') as f:                mail.Body = f.read()            mail.Send()            window.add_status_label("Email verstuurd")        else:            log_file.close()            send_mail(file_path)    except Exception as e:        with open(file_path, 'w') as file:            file.write('Mislukt om email te sturen: ' + str(e))        window.add_status_label("Mislukt om email te sturen")def everything_whent_well():    window.searching_for(' ')    i = window.ask_question('Is alles goed gegaan?: (Y/N) \n')    if i.upper() == 'Y':        again()    elif i.upper() == 'N':        data = window.ask_question('Wat is er precies fout gegaan?: \n')        if data is not None and data != '':            log_file.write('Opmerking: ' + data + '\n')            send_mail(log_file.name)            again()        else:            window.alert('Er is wat fout gegaan, we proberen het opnieuw')            everything_whent_well()    else:        everything_whent_well()def main():    window.set_running_main(True)    window.clear_found_object()    window.add_logs()    find_email()    filter_data()    # log_file.write('Woordenlijst: ' + w_list.__str__() + '\n')    # get_client()    # json_values = data_filter.filter_data(client, log_file, window, w_list, json_values)    # create_project()    # everything_whent_well()    if os.path.exists("file.pdf"):        os.remove("file.pdf")    if not log_file.closed:        log_file.close()    window.add_logs()    window.set_running_main(False)def find_title_loop():    while not window.running_main:        try:            outlook = win32com.client.Dispatch("Outlook.Application")            selection = outlook.ActiveExplorer().Selection            if selection.Count > 0:                message = selection.Item(1)                window.set_titel(message.subject)            if window.run_main_again:                window.run_main_again = False                main()            if window.send_email != '':                send_mail('Logs/' + window.send_email)                window.send_email = ''        except Exception as e:            log_file.write('Fout bij het vinden van een email: ' + str(e) + '\n')            window.set_titel("*Nog geen email titel kunnen vinden*")ctx = ssl.create_default_context(cafile=certifi.where())geopy.geocoders.options.default_ssl_context = ctxlog_file = open(f'Logs/{datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S")}.txt', 'w')results = []client = ''json_values = []w_list = []if os.path.exists("file.pdf"):    os.remove("file.pdf")if os.path.exists("image.png"):    os.remove("image.png")app = QApplication(sys.argv)window = gui.MainWindow()thread_1 = threading.Thread(target=window.show())thread_2 = threading.Thread(target=main())thread_3 = threading.Thread(target=find_title_loop())thread_1.start()thread_2.start()thread_3.start()app.exec()