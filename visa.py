# -*- coding: utf8 -*-

# Original script: https://gist.github.com/Svision/04202d93fb32d14f00ac746879820722

import time
import json
import random
from datetime import datetime
from os import system
import argparse

import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-u', '--username', type=str, required=True, help='Username')
# Note: It's a security risk to pass in password this way as anyone who can run `ps` will see the password, but w/e...
parser.add_argument('-p', '--password', type=str, required=True, help='Password')
parser.add_argument('-s', '--schedule', type=int, required=True, help='8-digit schedule name.')
parser.add_argument('-d', '--date', required=False, default='2023-03-07',
                    help='Date in YYYY-MM-DD format. Only notify if appointments earlier than this is found.')

args = parser.parse_args()


QUERY_INTERVAL_IN_SEC = 180   # recheck time interval

DATE_URL_TMPL = "https://ais.usvisa-info.com/en-ca/niv/schedule/%s/appointment/days/%d.json?appointments[expedite]=false"
LOCATION_MAP = {89: 'calgary', 90: 'helifax', 91: 'montreal', 92: 'ottawa', 93: 'quebec city', 94: 'toronto', 95: 'vancouver'}



def get_drive():
    dr = webdriver.Chrome(executable_path = 'chromedriver')
    return dr

driver = get_drive()


def login():
    # Bypass reCAPTCHA
    driver.get("https://ais.usvisa-info.com/en-ca/niv")
    time.sleep(1)
    a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(1)

    print("start signing in")
    href = driver.find_element(By.XPATH, '//*[@id="header"]/nav/div[2]/div[1]/ul/li[3]/a')
    href.click()
    # print("DEBUG: " + driver.get_cookie("_yatri_session")["value"])
    Wait(driver, 60).until(EC.presence_of_element_located((By.NAME, "commit")))

    print("click bounce")
    a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(1)

    do_login_action()


def do_login_action():
    print("input email")
    user = driver.find_element(By.ID, 'user_email')
    user.send_keys(args.username)
    time.sleep(random.randint(1, 3))

    print("input pwd")
    pw = driver.find_element(By.ID, 'user_password')
    pw.send_keys(args.password) 
    time.sleep(random.randint(1, 3))

    print("click privacy")
    box = driver.find_element(By.CLASS_NAME, 'icheckbox')
    box .click()
    time.sleep(random.randint(1, 3))

    print("commit")
    btn = driver.find_element(By.NAME, 'commit')
    btn.click()
    time.sleep(random.randint(1, 3))

    # print("DEBUG: " + driver.get_cookie("_yatri_session")["value"])

    Wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Continue')]")))
    print("Login successfully! ")


def get_date(location):
    driver.get(DATE_URL_TMPL % (args.schedule, location))
    if not is_logined():
        login()
        return get_date(location)
    else:
        content = driver.find_element(By.TAG_NAME, 'pre').text
        date = json.loads(content)
        return date


def is_logined():
    content = driver.page_source
    if(content.find("error") != -1):
        return False
    return True


def print_date(dates):
    for d in dates:
        print("%s \t business_day: %s" %(d.get('date'), d.get('business_day')))


def get_available_date(dates):
    def is_earlier(date):
        return datetime.strptime(args.date, "%Y-%m-%d") > datetime.strptime(date, "%Y-%m-%d")

    for d in dates:
        date = d.get('date')
        if is_earlier(date):
            return date


def push_notification(dates):
    PUSHOVER_TOKEN = '<my push token>'
    PUSHOVER_USER = '<my push user>'
    msg = "date: "
    for d in dates:
        msg = msg + d.get('date') + '; '
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "message": msg
    }
    requests.post(url, data)


if __name__ == "__main__":
    login()
    retry_count = 0
    start_loc, end_loc = min(LOCATION_MAP.keys()), max(LOCATION_MAP.keys())
    while 1:
        if retry_count > 6:
            break
        try:
            print()
            print(datetime.today())
            print("------------------")
            for location in range(start_loc, end_loc):
                dates = get_date(location)[:5]
                print(f'{LOCATION_MAP[location]} has dates: {dates}')
                date = get_available_date(dates)
                if date:
                    # TODO: `say` is a command in Mac, feel free to replace with other way of doing notification.
                    system('say Date {} is available at {}'.format(date[0], LOCATION_MAP[location]))
                    print(f'Location: {location} - {LOCATION_MAP[location]} \t Good dates {date}')
                    print_date(dates)
                    push_notification(date)

            time.sleep(QUERY_INTERVAL_IN_SEC)
        except:
            retry_count += 1
            time.sleep(60)
