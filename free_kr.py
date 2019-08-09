import os
import sys
import time

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    acc_name = os.getenv('KRUNKER_ACC_NAME')
    acc_pw = os.getenv('KRUNKER_ACC_PW')
    if not acc_name or not acc_pw:
        print('Env variables KRUNKER_ACC_NAME and KRUNKER_ACC_PW are not found')
        sys.exit(1)

    # don't wait full page load
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"
    driver = webdriver.Remote(
        command_executor='http://127.0.0.1:4444/wd/hub',
        desired_capabilities=caps
    )

    try:
        driver.get("https://krunker.io")
        accept_cookies(driver)
        login(driver, acc_name, acc_pw)
        watch_ad(driver)

    finally:
        driver.quit()


def accept_cookies(driver):
    print('Accept cookies ...')
    accept_btn = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((
            By.XPATH,
            '//*[@id="consentWindow"]/*/div[text()="Accept"]'
        ))
    )
    accept_btn.click()


def login(driver, acc_name, acc_pw):
    print('Open login window')
    btn = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((
            By.XPATH,
            '//*[@id="signedOutHeaderBar"]/*[text()="Login"]'
        ))
    )
    btn.click()
    print('Input credentials')
    time.sleep(1)
    # Input credentials
    name_input = driver.find_element_by_id('accName')
    name_input.send_keys(acc_name)
    pw_input = driver.find_element_by_id('accPass')
    pw_input.send_keys(acc_pw)
    btn = driver.find_element_by_xpath(
        '//*[@id="menuWindow"]/*[text()="Login"]'
    )
    btn.click()


def watch_ad(driver):
    print('Click "Free KR" button')
    free_kr_btn_id = 'claimHolder'
    free_kr_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, free_kr_btn_id))
    )
    free_kr_btn.click()
    print('Watch ad')
    time.sleep(60)


if __name__ == '__main__':
    main()
