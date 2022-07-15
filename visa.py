# -*- coding: utf8 -*-

# Source: https://gist.github.com/Svision/04202d93fb32d14f00ac746879820722
import time
import json
import random
import platform
from datetime import datetime
from os import system

import requests
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


USERNAME = '<username>'
PASSWORD = '<password>'
SCHEDULE = '37089586'

PUSH_TOKEN = '<my push token>'
PUSH_USER = '<my push user>'

MY_SCHEDULE_DATE = "2023-03-07" # 2020-12-02
MY_CONDITION = lambda month,day: int(month) == 11 and int(day) >= 5

SLEEP_TIME = 180   # recheck time interval

DATE_URL_TMPL = "https://ais.usvisa-info.com/en-ca/niv/schedule/%s/appointment/days/%d.json?appointments[expedite]=false"
LOCATION_MAP = {89: 'calgary', 90: 'helifax', 91: 'montreal', 92: 'ottawa', 93: 'quebec city', 94: 'toronto', 95: 'vancouver'}

# TIME_URL = "https://ais.usvisa-info.com/en-ca/niv/schedule/%s/appointment/times/95.json?date=%%s&appointments[expedite]=false" % SCHEDULE
# APPOINTMENT_URL = "https://ais.usvisa-info.com/en-ca/niv/schedule/%s/appointment" % SCHEDULE

def send(msg):
    url = "https://api.pushover.net/1/messages.json"
    data = {
        "token": PUSH_TOKEN,
        "user": PUSH_USER,
        "message": msg
    }
    requests.post(url, data)


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

    print("start sign")
    href = driver.find_element(By.XPATH, '//*[@id="header"]/nav/div[2]/div[1]/ul/li[3]/a')
    href.click()
    # time.sleep(5)
    # print(driver.get_cookie("_yatri_session")["value"])
    Wait(driver, 60).until(EC.presence_of_element_located((By.NAME, "commit")))

    print("click bounce")
    a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(1)

    do_login_action()


def do_login_action():
    print("input email")
    user = driver.find_element(By.ID, 'user_email')
    user.send_keys(USERNAME)
    time.sleep(random.randint(1, 3))

    print("input pwd")
    pw = driver.find_element(By.ID, 'user_password')
    pw.send_keys(PASSWORD) 
    time.sleep(random.randint(1, 3))

    print("click privacy")
    box = driver.find_element(By.CLASS_NAME, 'icheckbox')
    box .click()
    time.sleep(random.randint(1, 3))

    print("commit")
    btn = driver.find_element(By.NAME, 'commit')
    btn.click()
    time.sleep(random.randint(1, 3))

    # time.sleep(5)
    # print(driver.get_cookie("_yatri_session")["value"])

    Wait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(),'Continue')]")))
    print("Login successfully! ")


def get_date(location):
    driver.get(DATE_URL_TMPL % (SCHEDULE, location))
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
        return datetime.strptime(MY_SCHEDULE_DATE, "%Y-%m-%d") > datetime.strptime(date, "%Y-%m-%d")

    for d in dates:
        date = d.get('date')
        if is_earlier(date):
            # year, month, day = date.split('-')
            # if(MY_CONDITION(month, day)):
            #     last_seen = date
            return date


def push_notification(dates):
    msg = "date: "
    for d in dates:
        msg = msg + d.get('date') + '; '
    send(msg)


if __name__ == "__main__":
    login()
    retry_count = 0
    while 1:
        if retry_count > 6:
            break
        try:
            print()
            print(datetime.today())
            print("------------------")
            for location in range(89,96):
                dates = get_date(location)[:5]
                date = get_available_date(dates)
                if date:
                    system('say Date {} is available at {}'.format(date[0], LOCATION_MAP[location]))
                    print('Location: ', location, LOCATION_MAP[location], '; \tGood dates: ', date)
                    print_date(dates)

            time.sleep(SLEEP_TIME)
        except:
            retry_count += 1
            time.sleep(60)
