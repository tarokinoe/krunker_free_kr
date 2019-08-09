import argparse
import logging
import json
import socket
import sys
import time

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


with open('settings.json') as f:
    settings = json.load(f)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


def wait_for_host_becoming_available(host, port):
    logger.info('Wait for host becoming available')
    attempts = 0
    while True:
        attempts += 1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        if result == 0:
            break
        else:
            if attempts > 12:
                break
            time.sleep(5)


def main(args):
    acc_name = settings.get('KRUNKER_ACC_NAME')
    acc_pw = settings.get('KRUNKER_ACC_PW')
    if not acc_name or not acc_pw:
        logger.info(
            'Settings KRUNKER_ACC_NAME and KRUNKER_ACC_PW are not found'
        )
        sys.exit(1)

    # don't wait full page load
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "none"

    while True:
        logger.info('Start')
        if args.debug:
            driver = webdriver.Chrome(desired_capabilities=caps)
        else:
            wait_for_host_becoming_available(
                host="google_chrome_standalone",
                port=4444
            )
            driver = webdriver.Remote(
                command_executor='http://google_chrome_standalone:4444/wd/hub',
                desired_capabilities=caps
            )
        try:
            driver.get("https://krunker.io")
            accept_cookies(driver)
            login(driver, acc_name, acc_pw)
            watch_ad(driver)
        finally:
            logger.info('Driver quit')
            driver.quit()

        logger.info('Sleeping...')
        if args.debug:
            time.sleep(10)
        else:
            time.sleep(60 * 60 * 6 + 60 * 5)  # 6h 5m


def accept_cookies(driver):
    logger.info('Accept cookies')
    accept_btn = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((
            By.XPATH,
            '//*[@id="consentWindow"]/*/div[text()="Accept"]'
        ))
    )
    accept_btn.click()


def login(driver, acc_name, acc_pw):
    logger.info('Open login window')
    btn = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((
            By.XPATH,
            '//*[@id="signedOutHeaderBar"]/*[text()="Login"]'
        ))
    )
    btn.click()
    logger.info('Input credentials')
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
    logger.info('Click "Free KR" button')
    free_kr_btn_id = 'claimHolder'
    free_kr_btn = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.ID, free_kr_btn_id))
    )
    free_kr_btn.click()
    logger.info('Watch ad')
    time.sleep(60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    main(args)
