import time
from BaseExtractor import BaseExtractor
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import pandas as pd
import itertools
import json
import schedule
from schedule import every, repeat
import os
from datetime import datetime
import re

# TODO - Keep table updated | Search
# from base import Base

options = Options()
options.headless = True
options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
PATH = "C:/Program Files (x86)/geckodriver.exe"
driver = webdriver.Firefox(executable_path=PATH, options=options)
driver.maximize_window()
url = 'https://www.iaa.gov.il/en/airports/ben-gurion/flight-board/'


def close():
    driver.close()
    driver.quit()

    # search("RYANAIR")


class FlightExtractor(BaseExtractor):
    @repeat(every(1).minutes)
    def get_data(self):
        driver.get(url)
        # Get the table headers
        table_headers = WebDriverWait(driver, 10).until(
            EC.visibility_of_any_elements_located(
                (By.XPATH, "//table[@id='flight_board-arrivel_table']//thead//tr//th")))

        # Put headers names into a list
        columns = list(map(lambda name: name.text, table_headers))

        # Click on show more until button is gone
        while True:
            try:
                WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@id='next']"))).click()
            except:
                break

        # Get the table rows
        table = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='flight_board-arrivel_table']")))

        # Put the rows into a list
        list_to_break = [cell.text for row in table.find_elements_by_css_selector('tr') for cell in
                         row.find_elements_by_tag_name('td')]

        # Break the list into a nested list - each list is a row
        result = [list(v) for k, v in itertools.groupby(list_to_break, key=lambda sep: sep == "") if not k]

        # Insert into Pandas Dataframe.
        df_flights = pd.DataFrame(result, columns=columns)

        # Convert table to json.
        flights_json = df_flights.to_json(orient='table', indent=4)

        # Storing the data extracted
        now = datetime.now()
        dt_string = now.strftime("%m-%d-%y_%H-%M-%S")
        with open(f'C:/Users/Gil/PycharmProjects/Matrix_Selenium/ft{dt_string}.json', "w+") as file:
            json.dump(flights_json, file)

        driver.refresh()

    def search(self, expression, file_type='.json'):
        self.search(expression, file_type)

    @staticmethod
    def main():
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    main()
