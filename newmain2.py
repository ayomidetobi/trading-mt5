import os
import os.path
from datetime import datetime
from time import sleep
import pandas as pd
import pytz as pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from mongo_db import DbConnect
from selenium.webdriver.common.keys import Keys


def get_all_accounts():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    # If modifying these scopes, delete the file token.json.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    # The ID and range of a sample spreadsheet.
    if os.getenv("SPREADSHEET_ID") is None:
        SPREADSHEET_ID = "1-OUeYL276pdmlOnOhC1mQMKBYP_HhybJqeDJbWLsBTo"
        RANGE_NAME = "Sheet1"
    else:
        SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
        RANGE_NAME = os.getenv("SPREADSHEET_NAME")

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("server_keys.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return
        else:
            return values[1:]
    except HttpError as err:
        print(err)


def get_new_tab():
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--no-sandbox")
    opts.add_experimental_option("windowTypes", ["webview"])
    opts.add_argument("accept-language=en-GB,en;q=0.9,en-US;q=0.8")
    opts.add_argument("cache-control=no-cache")
    opts.add_argument("pragma=no-cache")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"
    )
    opts.add_argument("--start-maximized")
    opts.add_argument("--headless")

    # starting service for chrome web driver
    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    service = Service(executable_path=ChromeDriverManager().install())
    # initiating chrome web driver
    web_browser = webdriver.Chrome(
        options=opts,
        service=service,
    )
    return web_browser


def get_market_date(server_name):
    server_list = [
        "Deriv-Demo",
        "ForexTimeFXTM-Demo01",
        "ForexTimeFXTM-ECN-Demo",
        "ICMarketsSC-Demo02",
        "HugosWay-Demo03",
    ]
    gtm0_timezone = pytz.timezone("GMT+0")
    gtm2_timezone = pytz.timezone("Europe/Kiev")
    gtm3_timezone = pytz.timezone("Asia/Bahrain")

    market_date = datetime.now(gtm0_timezone).strftime("%Y-%m-%d %H:%M:%S")

    if server_name in server_list:

        if server_name in server_list[0]:
            market_date = datetime.now(gtm0_timezone).strftime("%Y-%m-%d %H:%M:%S")
        elif server_name in server_list[1]:
            market_date = datetime.now(gtm2_timezone).strftime("%Y-%m-%d %H:%M:%S")
        elif server_name in server_list[2]:
            market_date = datetime.now(gtm3_timezone).strftime("%Y-%m-%d %H:%M:%S")
        elif server_name in server_list[3]:
            market_date = datetime.now(gtm3_timezone).strftime("%Y-%m-%d %H:%M:%S")
        elif server_name in server_list[4]:
            market_date = datetime.now(gtm3_timezone).strftime("%Y-%m-%d %H:%M:%S")
        else:
            print("No server name matched.")
    else:
        print("No server found.")
    return market_date


# program starts from here
if __name__ == "__main__":

    base_url = "https://trade.mql5.com/trade"
    base_urlmt5 = "https://trade.mql5.com/trade?version=5"

    login_css = '[id="login"]'
    pass_css = '[id="password"]'
    server_css = 'input[id="server"]'
    market_watch_xpath = (
        '//div[@class="page-window market-watch compact"]/div/div[@class="h"]'
    )
    market_watch_css = "body > div.page-window.market-watch.compact > div > div.h"
    b_e_mt5_xpath = '//tr[@id="total"]/td[@id="symbol"]/div/span'
    b_e_mt4_xpath = '//div[@class="page-table grid fixed odd trade-table toolbox-table"][2]//tr[@class="total"]/td[1]/div/span'
    platform_mt4_css = 'input[type="radio"][id="mt4-platform"]'
    platform_mt5_css = 'input[type="radio"][id="mt5-platform"]'
    ok_button_xpath = '//button[text()="OK"]'
    b_e_mt4_css = " body > div.page-block.frame.bottom > div:nth-child(3) > table > tbody > tr.total > td.iconed > div > span"
    # /html/body/div[6]/div[3]/table/tbody/tr[6]/td[1]/div/span
    # /html/body/div[6]/div[3]/table/tbody/tr[6]/td[1]/div/span
    # /html/body/div[6]/div[3]/table/tbody/tr[6]/td[1]/div/span
    # body > div.page-block.frame.bottom > div:nth-child(3) > table > tbody > tr.total > td.iconed > div > span
    # while True:
    account_details = get_all_accounts()

    def mt4():
        browser.get(base_url)
        browser.implicitly_wait(15)
        platform4 = WebDriverWait(browser, 30).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, platform_mt4_css))
        )
        ActionChains(browser).move_to_element(platform4).click().perform()
        b_e_xpath = b_e_mt4_xpath
        print("MT4 clicked.")
        sleep(0.5)
        browser.implicitly_wait(20)
        WebDriverWait(browser, 20).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, login_css))
        ).send_keys(login_details[0])
        browser.implicitly_wait(10)
        WebDriverWait(browser, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, pass_css))
        ).send_keys(login_details[1])
        browser.implicitly_wait(10)
        server_input = WebDriverWait(browser, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, server_css))
        )
        server_input.clear()
        server_input.send_keys(login_details[2])
        login_button = WebDriverWait(browser, 30).until(
            ec.element_to_be_clickable((By.XPATH, ok_button_xpath))
        )
        ActionChains(browser).move_to_element(login_button).click().perform()
        print("should be logged in.")
        sleep(15.5)
        browser.implicitly_wait(70)
        print("should  clicked login")
        balance_equ_ele = WebDriverWait(browser, 25).until(
            ec.presence_of_element_located((By.XPATH, b_e_xpath))
        )
        sleep(4.5)
        try:
            balance_equity2 = balance_equ_ele.text.split(":")
        except Exception as e:
            pass

        browser.execute_script("arguments[0].scrollIntoView(true);", balance_equ_ele)
        ActionChains(browser).move_to_element(balance_equ_ele).perform()
        sleep(0.5)
        market_watch_time_ele = WebDriverWait(browser, 25).until(
            ec.presence_of_element_located((By.XPATH, market_watch_xpath))
        )
        result_dict = dict()
        print(balance_equ_ele.text.split(":"), "1sr")
        if market_watch_time_ele is not None:
            print(f"Login Account: {login_details[0]} logged in.")
            sleep(1)
            print(balance_equ_ele.text.split(":"))
            if balance_equ_ele is not None:

                balance_equity = balance_equ_ele.text.split(":")

                balance = (
                    balance_equity[1]
                    .replace("USD  Equity", "")
                    .replace(" ", "")
                    .strip()
                )

                equity = (
                    balance_equity[2]
                    .replace("Free margin", "")
                    .replace("Margin", "")
                    .replace(" ", "")
                    .strip()
                )

                result_dict["date"] = (
                    datetime.strptime(
                        get_market_date(login_details[2]),
                        "%Y-%m-%d %H:%M:%S",
                    )
                    .astimezone(pytz.timezone("Africa/Brazzaville"))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                result_dict["balance"] = balance
                result_dict["equity"] = equity
                print(result_dict)
            else:
                result_dict["date"] = (
                    datetime.strptime(
                        get_market_date(login_details[2]),
                        "%Y-%m-%d %H:%M:%S",
                    )
                    .astimezone(pytz.timezone("Africa/Brazzaville"))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                result_dict["balance"] = 0
                result_dict["equity"] = 0
            print(result_dict)
            con = DbConnect()
            new_insert_id = con.add_rows(str(login_details[0]), result_dict)
            print(
                f"Record inserter successfully. Inserted object id: {new_insert_id.inserted_id}"
            )
            con.close_con()
        else:
            print("No records available.")
        print(result_dict)
        print("Logging out..")
        browser.quit()

    def scroll():
        if market_watch_time_ele is not None:
            print(f"Using presaved")
            sleep(1)
            if balance_equity2 is not None:
                balance_equity = balance_equity2
                balance = (
                    balance_equity[1]
                    .replace("USD  Equity", "")
                    .replace(" ", "")
                    .strip()
                )
                equity = (
                    balance_equity[2]
                    .replace("Free margin", "")
                    .replace("Margin", "")
                    .replace(" ", "")
                    .strip()
                )
                result_dict["date"] = (
                    datetime.strptime(
                        get_market_date(login_details[2]),
                        "%Y-%m-%d %H:%M:%S",
                    )
                    .astimezone(pytz.timezone("Africa/Brazzaville"))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                result_dict["balance"] = balance
                result_dict["equity"] = equity
            else:
                result_dict["date"] = (
                    datetime.strptime(
                        get_market_date(login_details[2]),
                        "%Y-%m-%d %H:%M:%S",
                    )
                    .astimezone(pytz.timezone("Africa/Brazzaville"))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                result_dict["balance"] = 0
                result_dict["equity"] = 0
            con = DbConnect()
            new_insert_id = con.add_rows(str(login_details[0]), result_dict)
            print(
                f"Record inserter successfully. Inserted object id: {new_insert_id.inserted_id}"
            )
            con.close_con()

        else:
            print("No records available.")
        print(result_dict)
        print("Logging out..")
        browser.quit()

    def mt5():
        browser.get(base_urlmt5)
        browser.implicitly_wait(15)
        platform5 = WebDriverWait(browser, 30).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, platform_mt5_css))
        )
        browser.execute_script("arguments[0].click();", platform5)
        b_e_xpath = b_e_mt5_xpath
        sleep(2.5)
        print("MT5 clicked.")
        accept_button = WebDriverWait(browser, 10).until(
            ec.element_to_be_clickable((By.ID, "accept"))
        )
        ActionChains(browser).move_to_element(accept_button).click().perform()
        print("should have clicked accept")
        browser.implicitly_wait(20)
        WebDriverWait(browser, 20).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, login_css))
        ).send_keys(login_details[0])
        browser.implicitly_wait(10)
        WebDriverWait(browser, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, pass_css))
        ).send_keys(login_details[1])
        browser.implicitly_wait(10)
        server_input = WebDriverWait(browser, 30).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, server_css))
        )
        server_input.clear()
        server_input.send_keys(login_details[2])
        login_button = WebDriverWait(browser, 30).until(
            ec.element_to_be_clickable((By.XPATH, ok_button_xpath))
        )
        ActionChains(browser).move_to_element(login_button).click().perform()
        print("should have clicked login")
        sleep(15.5)
        browser.implicitly_wait(70)
        print("should  clicked login")
        balance_equ_ele = WebDriverWait(browser, 45).until(
            ec.presence_of_element_located((By.XPATH, b_e_xpath))
        )
        sleep(4.5)
        browser.implicitly_wait(31)
        try:
            balance_equity2 = balance_equ_ele.text.split(":")
            print(balance_equity2)
            equity = (
                balance_equity2[2]
                .replace("Free margin", "")
                .replace("Margin", "")
                .replace(" ", "")
                .strip()
            )
            if equity == "0.00":
                print("Shitt")
                balance_equ_ele = WebDriverWait(browser, 45).until(
                    ec.presence_of_element_located((By.XPATH, b_e_xpath))
                )
            balance_equity2 = balance_equ_ele.text.split(":")
        except Exception as e:
            print(e)
            pass
        browser.execute_script("arguments[0].scrollIntoView(true);", balance_equ_ele)
        ActionChains(browser).move_to_element(balance_equ_ele).perform()
        sleep(0.5)
        market_watch_time_ele = WebDriverWait(browser, 25).until(
            ec.presence_of_element_located((By.XPATH, market_watch_xpath))
        )
        browser.implicitly_wait(15)
        result_dict = dict()
        if market_watch_time_ele is not None:
            print(f"Login Account: {login_details[0]} logged in.")
            sleep(1)
            if balance_equ_ele is not None:
                balance_equity = balance_equ_ele.text.split(":")
                balance = (
                    balance_equity[1]
                    .replace("USD  Equity", "")
                    .replace(" ", "")
                    .strip()
                )
                equity = (
                    balance_equity[2]
                    .replace("Free margin", "")
                    .replace("Margin", "")
                    .replace(" ", "")
                    .strip()
                )
                result_dict["date"] = (
                    datetime.strptime(
                        get_market_date(login_details[2]),
                        "%Y-%m-%d %H:%M:%S",
                    )
                    .astimezone(pytz.timezone("Africa/Brazzaville"))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                result_dict["balance"] = balance
                result_dict["equity"] = equity
            else:
                result_dict["date"] = (
                    datetime.strptime(
                        get_market_date(login_details[2]),
                        "%Y-%m-%d %H:%M:%S",
                    )
                    .astimezone(pytz.timezone("Africa/Brazzaville"))
                    .strftime("%Y-%m-%d %H:%M:%S")
                )
                result_dict["balance"] = 0
                result_dict["equity"] = 0
            con = DbConnect()
            new_insert_id = con.add_rows(str(login_details[0]), result_dict)
            print(
                f"Record inserter successfully. Inserted object id: {new_insert_id.inserted_id} "
            )
            con.close_con()
            browser.quit()
        else:
            print("No records available.")
        print(result_dict)
        print("Logging out..")
        browser.quit()

    # account_details = pd.read_csv("test1.csv")
    while True:
        for login_details in account_details[:270]:
            sleep(1.0)
            browser = get_new_tab()
            browser.delete_all_cookies()
            b_e_xpath = ""
            if login_details[3] == "MT4":
                try:
                    mt4()
                except TimeoutException as e:
                    print(
                        f"Authorization Failed for {login_details[0]} account number. Trying again.."
                    )
                    browser.quit()
                except StaleElementReferenceException:
                    print("Cant Scroll")
                    try:
                        mt4()
                    except Exception as e:
                        scroll()
                        browser.quit()
                    browser.quit()

                except Exception as e:
                    # print(traceback.print_tb(e.__traceback__))
                    print("Exceptions raised.")
                    browser.quit()

            if login_details[3] == "MT5":
                try:
                    mt5()
                except TimeoutException as e:
                    print(
                        f"Authorization Failed for {login_details[0]} account number. Trying again.."
                    )
                    browser.quit()
                except StaleElementReferenceException:
                    print("Cant Scroll")
                    scroll()
                    browser.quit()

                except Exception as e:
                    # print(traceback.print_tb(e.__traceback__))
                    print("Exceptions raised.", e)
                    browser.quit()
