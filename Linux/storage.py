import csv
import datetime


class Storage(object):
    def __init__(self) -> None:
        self.__filename = ''
        self.create()

    # create new csv, first line data with
    # Test time, QR Code, 'Device name', 'Model Name', 'Result']
    def create(self) -> None:
        self.__filename = self.__get_datetime()
        title = ['Test Time', 'QR Code', 'File Name', 'Device Name', 'Model Name', 'Result']
        with open(self.filename, 'w', newline='') as file:
            csv_write = csv.writer(file)
            csv_write.writerow(title)

    # params: data is dict
    # keywords: time, code, device, model, result
    def write(self, **kwargs) -> None:
        data = {}
        for key, value in kwargs.items():
            data[key] = value
        with open(self.filename, 'a', newline='') as file:
            csv_write = csv.writer(file)
            csv_write.writerow([data['time'], data['code'], data['filename'], data['device'], data['model'], data['result']])

    @property
    def filename(self) -> str:
        return self.__filename + '.csv'

    @staticmethod
    def __get_datetime() -> str:
        name = datetime.datetime.now().strftime("%Y%m%d%H%M")
        return name
