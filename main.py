import os
import threading
import concurrent.futures
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
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from mongo_db import DbConnect


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
    # service = Service(executable_path=ChromeDriverManager().install())
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


def get_data(account_details):
    base_url = "https://trade.mql5.com/trade"
    base_urlmt5 = "https://trade.mql5.com/trade?version=5"

    login_css = '[id="login"]'
    pass_css = '[id="password"]'
    server_css = 'input[id="server"]'
    market_watch_xpath = (
        '//div[@class="page-window market-watch compact"]/div/div[@class="h"]'
    )
    b_e_mt4_xpath = '//div[@class="page-table grid fixed odd trade-table toolbox-table"][2]//tr[@class="total"]/td[1]/div/span'
    b_e_mt5_xpath = '//tr[@id="total"]/td[@id="symbol"]/div/span'
    # /html/body/div[6]/div[3]/table/tbody/tr/td[1]/div/span
    # /html/body/div[6]/div[3]/table/tbody/tr/td[1]/div/span/text()
    # /html/body/div[6]/div[3]/table/tbody/tr/td[1]/div/span
    # //td[@id="symbol"]
    platform_mt4_css = 'input[type="radio"][id="mt4-platform"]'
    platform_mt5_css = 'input[type="radio"][id="mt5-platform"]'
    ok_button_xpath = '//button[text()="OK"]'

    # for login_details in account_details:
    sleep(1.0)
    print("it is")
    browser = get_new_tab()
    browser.delete_all_cookies()
    browser.refresh()
    b_e_xpath = ""
    print("it is again")
    if account_details[3] == "MT4":
        try:
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
            ).send_keys(account_details[0])
            browser.implicitly_wait(10)
            WebDriverWait(browser, 30).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, pass_css))
            ).send_keys(account_details[1])
            browser.implicitly_wait(10)
            server_input = WebDriverWait(browser, 30).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, server_css))
            )
            server_input.clear()
            server_input.send_keys(account_details[2])
            login_button = WebDriverWait(browser, 30).until(
                ec.element_to_be_clickable((By.XPATH, ok_button_xpath))
            )
            ActionChains(browser).move_to_element(login_button).click().perform()
            print("should be logged in.")
            sleep(3.5)
            browser.implicitly_wait(10)
            balance_equ_ele = WebDriverWait(browser, 25).until(
                ec.presence_of_element_located((By.XPATH, b_e_xpath))
            )
            sleep(0.5)
            market_watch_time_ele = WebDriverWait(browser, 25).until(
                ec.presence_of_element_located((By.XPATH, market_watch_xpath))
            )

            result_dict = dict()
            if market_watch_time_ele is not None:
                print(f"Login Account: {account_details[0]} logged in.")
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
                            get_market_date(account_details[2]),
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
                            get_market_date(account_details[2]),
                            "%Y-%m-%d %H:%M:%S",
                        )
                        .astimezone(pytz.timezone("Africa/Brazzaville"))
                        .strftime("%Y-%m-%d %H:%M:%S")
                    )
                    result_dict["balance"] = 0
                    result_dict["equity"] = 0
                con = DbConnect()
                new_insert_id = con.add_rows(str(account_details[0]), result_dict)
                print(
                    f"Record for {account_details[0]} inserted successfully. Inserted object id: {new_insert_id.inserted_id}"
                )
                con.close_con()
            else:
                print("No records available.")
            print(result_dict)
            print("Logging out..")
            browser.quit()
        except TimeoutException as e:
            print(
                f"Authorization Failed for mt4 {account_details[0]} account number. Trying again.."
            )
            browser.close()
            pass
        except Exception as e:
            # print(traceback.print_tb(e.__traceback__))
            print("Exceptions raised.")
            browser.close()
            pass

    if account_details[3] == "MT5":
        try:
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
            ).send_keys(account_details[0])
            browser.implicitly_wait(10)
            WebDriverWait(browser, 30).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, pass_css))
            ).send_keys(account_details[1])
            browser.implicitly_wait(10)
            server_input = WebDriverWait(browser, 30).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, server_css))
            )
            server_input.clear()
            server_input.send_keys(account_details[2])
            login_button = WebDriverWait(browser, 30).until(
                ec.element_to_be_clickable((By.XPATH, ok_button_xpath))
            )
            ActionChains(browser).move_to_element(login_button).click().perform()
            print("should have clicked login")
            sleep(9.5)
            WebDriverWait(browser, 25).until(
                ec.presence_of_element_located(
                    (By.XPATH, "//tr[@id='total']/td[@id='symbol']/div/span")
                )
            )
            balance_equ_ele = browser.find_element(
                by=By.XPATH, value="//tr[@id='total']/td[@id='symbol']/div/span"
            )
            browser.implicitly_wait(30)
            WebDriverWait(browser, 85).until(
                ec.presence_of_element_located(
                    (By.XPATH, "//tr[@id='total']/td[@id='symbol']/div/span")
                )
            )
            sleep(1.5)
            # omo = browser.find_element(
            #     by=By.XPATH, value="//tr[@id='total']/td[@id='symbol']/div/span"
            # )
            market_watch_time_ele = WebDriverWait(browser, 25).until(
                ec.presence_of_element_located((By.XPATH, market_watch_xpath))
            )
            print(balance_equ_ele, "bal", balance_equ_ele.text)
            print(
                market_watch_time_ele, "market watch time", market_watch_time_ele.text
            )
            result_dict = dict()
            if market_watch_time_ele is not None:
                print(f"Login Account: {account_details[0]} logged in.")
                sleep(5)
                if balance_equ_ele is not None:
                    sleep(5)
                    balance_equity = balance_equ_ele.text.split(":")
                    # print(list(balance_equity))
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
                            get_market_date(account_details[2]),
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
                            get_market_date(account_details[2]),
                            "%Y-%m-%d %H:%M:%S",
                        )
                        .astimezone(pytz.timezone("Africa/Brazzaville"))
                        .strftime("%Y-%m-%d %H:%M:%S")
                    )
                    result_dict["balance"] = 0
                    result_dict["equity"] = 0
                con = DbConnect()
                new_insert_id = con.add_rows(str(account_details[0]), result_dict)
                print(
                    f"Record for {account_details[0]} inserted successfully. Inserted object id: {new_insert_id.inserted_id}"
                )
                con.close_con()
            else:
                print("No records available.")
            print(result_dict)
            print("Logging out..")
            browser.quit()
        except TimeoutException as e:
            print(
                f"Authorization Failed for mt5 {account_details[0]} account number. Trying again.."
            )
            browser.refresh()
        except StaleElementReferenceException as e:
            print(e)
            browser.refresh()
        except Exception as e:
            # print(traceback.print_tb(e.__traceback__))
            print("Exceptions raised.", e)
            pass


if __name__ == "__main__":
    while True:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            print("Starting..")
            account_details = get_all_accounts()
            # account_details = pd.read_csv("test1.csv")
            print("Starting again..")
            # print(account_details[:4])
            results = executor.map(get_data, account_details[:45])

        # threads = []
        # account_detailss = get_all_accounts()
        # # tr = threading.Thread(target=get_data, args=(account_details[0],))
        # for account_details in account_detailss[:9]:
        #     tr = threading.Thread(target=get_data, args=(account_details,))
        #     print(account_details)
        #     tr.start()
        #     threads.append(tr)
        # for thread in threads:
        #     thread.join()
