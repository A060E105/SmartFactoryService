# from config import Configuration
# =======================================================
#                   public variable
# =======================================================
# CONFIG = Configuration()

import os
import csv
import numpy as np
import pandas as pd
import datetime


class TEDCSVAgent:

    def __init__(self, csv_folder_path, model_use_id, current_today, current_timestamp) -> None:
        self._csv_folder_path = csv_folder_path
        self._today = current_today
        self._current_timestamp = current_timestamp
        self._model_use_id = model_use_id

    def write_csv(self):
        file_name = f'{self._csv_folder_path}{self._model_use_id}/{self._today}.csv'

        # Append "xyz" to the file
        with open(file_name, 'a') as f:
            f.write(f'xyz, {self._current_timestamp} \n')


if __name__ == "__main__":
    csv_folder = "/Users/ted/Desktop/"
    today = datetime.date.today().strftime('%Y-%m-%d')
    cr_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    model_use_id = 'MODEL01'
    agent = TEDCSVAgent(csv_folder, model_use_id, today, cr_ts)
    agent.write_csv()
