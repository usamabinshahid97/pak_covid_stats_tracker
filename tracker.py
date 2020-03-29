from threading import Timer
import time
import requests
from bs4 import BeautifulSoup
import copy
import smtplib
emailList = ['xyz@abc.com']

def send_Mail(dct, death = False):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('email', 'password')
    if (death == True):
        subject = 'New death(s) reported in Pakistan!'
        body = '\nNew death(s) reported in Pakistan!!!\n'
    else:
        subject = 'Coronavirus stats in Pakistan!'
    body = '\n'
    for k, v in dct.items():
        if (k != 'last_updated_at' and k != 'death_count_increased'):
            if (k == 'Deaths'):
                if ("death_count_increased" in dct):
                    body += k.replace('_', ' ') + ' : ' + v + ' (+' + dct['death_count_increased'] + ')' + '\n'
                    continue
                else:
                    body += k.replace('_', ' ') + ' : ' + v + '\n'
                    continue
            body += k.replace('_', ' ') + ' : ' + v + '\n'
    body += '\n' + dct['last_updated_at']
    body += '\n\nThis is an automated generated email. All the stats have been obtained from the Government offical website. To unsubscribe reply back with empty message'
    for email in emailList:
        msg = f"Subject: {subject}\nTo: {email}\n\n{body}"
        server.sendmail('Coronavirus', email, msg)
        print('Hey Email has been sent to ', email)
    server.quit()
    

def extractLatestData(dct_old = False, checkpoint = 0):
    page = requests.get('http://covid.gov.pk/')
    soup = BeautifulSoup(page.text, 'html.parser')
    dct = {}
    dct['confirmed_cases'] = soup.find(class_='text-muted numbers-main').text
    overall_stats = soup.find(class_='text-center')
    recovered = 0
    critical = 0
    deaths = 0
    for main in overall_stats:
        if (main.name == 'div'):
            for inside in main:
                if (inside.name == 'div'):
                    for data in inside:
                        if (data.name == 'h6'):
                            title = data.text
                        if (data.name == 'h4'):
                            dct['%s'%title] = data.text

    provincial_stats = soup.find(class_='provinc-stat') 
    for main in provincial_stats:
        if (main.name == 'div'):
            for data in main:
                if (data.name == 'h6'):
                    title = data.text
                if (data.name == 'h4'):
                    dct['%s'%title] = data.text
    dct['last_updated_at'] = soup.find(id='date').text.lstrip('\n').lstrip(' ').rstrip(' ').rstrip('\n')
    if (dct_old):
        if (int(dct['Deaths']) > int(dct_old['Deaths'])):
            dct['death_count_increased'] = str(int(dct['Deaths']) - int(dct_old['Deaths']))
            send_Mail(dct, True) # Send mail if new death reported!
            del dct['death_count_increased']
    dct_old = copy.deepcopy(dct)
    if (checkpoint == 0):
        send_Mail(dct)
    if (checkpoint == 10800): # Send mail after very 3 hours
        send_Mail(dct)
        checkpoint = 0
    checkpoint += 600
    Timer(600, extractLatestData, [dct_old, checkpoint]).start() # 10 minutes timer

extractLatestData()