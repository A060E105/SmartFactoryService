import os
import csv
import datetime

# from config import Configuration
# =======================================================
#                   public variable
# =======================================================
# CONFIG = Configuration()


class CSVAgent:
    def __init__(self, model_name, model_version, current_timestamp: datetime.datetime) -> None:
        self.__model_name = model_name
        self.__model_version = model_version
        self.__current_timestamp = current_timestamp

    @property
    def filename(self):
        return self.__current_timestamp.strftime('%Y%m%d')

    def write_csv(self, **kwargs) -> None:
        data = {}
        for key, value in kwargs.items():
            data[key] = value

        if not os.path.exists(self.__file_path):
            self.__create_csv()
        with open(self.__file_path, 'a', newline='') as file:
            csv_write = csv.writer(file)
            csv_write.writerow([data.get('file_name'), data.get('ai_score1'), data.get('ai_score_2'),
                               data.get('freq_result'), data.get('ai_result'), data.get('final_result'),
                               data.get('created_at')])

    def __create_csv(self):
        self.__mkdir()
        title = ['file_name', 'ai_score1', 'ai_score_2', 'freq_result', 'ai_result', 'final_result', 'created_at']
        with open(self.__file_path, 'w', newline='') as file:
            csv_write = csv.writer(file)
            csv_write.writerow(title)

    @property
    def __file_path(self):
        return os.path.join('CSV', self.__model_name, self.__model_version, self.filename + '.csv')

    @staticmethod
    def __mkdir() -> None:
        path = os.path.join('./', 'CSV')
        try:
            os.makedirs(path)
        except Exception as e:
            pass


if __name__ == "__main__":
    csv_agent = CSVAgent(datetime.datetime.now())
    data = {'file_name': 'test', 'ai_score1': 'test', 'ai_score_2': 'test', 'freq_result': 'test', 'ai_result': 'test',
            'final_result': 'test', 'created_at': 'test'}
    csv_agent.write_csv(data)
