# coding=utf-8
"""
    author: Jin-Mo, Lin
    email: s106003041@g.ksu.edu.tw
    version: 1.0.0
    description: this is a smart factory configuration class,
        this class is a single instance, you can read and write
        configuration in any process.
"""

import json
import os


class Configuration:
    _instance = None
    filename = './SmartFactory.conf'

    # single instance
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.data = {}
        # if the file exist then read the file, else create the file
        if os.path.isfile(self.filename):
            self.read()
        else:
            self.create()
            self.save()

    @property
    def version(self) -> str:
        return self.data['version']

    @version.setter
    def version(self, new_version) -> None:
        self.data['version'] = new_version

    @property
    def model_name(self) -> str:
        return self.data['model_name']

    @property
    def device_name(self) -> str:
        return self.data['device_name']

    @property
    def mic_default_name(self) -> str:
        return self.data['device']['mic_default']['name']

    @property
    def mic_default_cali(self) -> float:
        return self.data['device']['mic_default']['calibration']

    @property
    def mic_1_name(self) -> str:
        return self.data['device']['mic_1']['name']

    @property
    def mic_1_cali(self) -> float:
        return self.data['device']['mic_1']['calibration']

    @property
    def mic_2_name(self) -> str:
        return self.data['device']['mic_2']['name']

    @property
    def mic_2_cali(self) -> float:
        return self.data['device']['mic_2']['calibration']

    @property
    def second(self) -> int:
        return self.data['audio']['second']

    @property
    def framerate(self) -> int:
        return self.data['audio']['framerate']

    @property
    def samples(self) -> int:
        return self.data['audio']['samples']

    @property
    def sampwidth(self) -> int:
        return self.data['audio']['sampwidth']

    @property
    def channels(self) -> int:
        return self.data['audio']['channels']

    @property
    def with_cut_file(self) -> bool:
        return self.data['spectrogram']['with_cut_file']

    @property
    def save_split_audio(self) -> bool:
        return self.data['spectrogram']['save_split_audio']

    @property
    def port(self) -> int:
        return self.data['server']['port']

    @property
    def status_message(self) -> list:
        return self.data['status_message']

    def set_cali(self, config_name: str, value: float) -> None:
        try:
            self.data['device'][config_name]['calibration'] = value
            self.save()
        except KeyError:        # if the device name is invalid or does not exist then not working
            pass

    def get_cali(self, config_name: str) -> float:
        try:
            cali = self.data['device'][config_name]['calibration']
            return cali
        except KeyError:
            pass

    # create configuration file
    def create(self) -> None:
        self.data['version'] = '1.0.0'
        self.data['model_name'] = 'model.h5'
        self.data['device_name'] = "A"
        # device settings
        self.data['device'] = {}
        self.data['device']['mic_default'] = {'name': 'Cotron EZM-001-2', 'calibration': 1}
        self.data['device']['mic_1'] = {'name': 'Cotron EZM-001-1', 'calibration': 1}
        self.data['device']['mic_2'] = {'name': 'Cotron EZM-001-2', 'calibration': 1}
        # audio settings
        self.data['audio'] = {}
        self.data['audio']['second'] = 5
        self.data['audio']['framerate'] = 96000
        self.data['audio']['samples'] = 4096
        self.data['audio']['sampwidth'] = 2
        self.data['audio']['channels'] = 1
        # spectrogram settings
        self.data['spectrogram'] = {}
        self.data['spectrogram']['with_cut_file'] = True
        self.data['spectrogram']['save_split_audio'] = False
        # server settings
        self.data['server'] = {}
        self.data['server']['port'] = 7000
        # status message
        self.data['status_message'] = {}
        self.data['status_message']['wait_for_press'] = '等待按下測試按鈕'
        self.data['status_message']['wait_for_scanner'] = '等待 QR Code 掃描'
        self.data['status_message']['wait_for_down'] = '汽缸作動中'
        self.data['status_message']['recording'] = '分析中'
        self.data['status_message']['calibration'] = '麥克風校正中'

    # read configuration file
    def read(self) -> None:
        with open(self.filename, 'r+', encoding='utf-8') as config:
            self.data = json.load(config)

    # save configuration to file
    def save(self) -> None:
        # using w+ mode open file, if the file does not exist then create the file
        with open(self.filename, 'w+', encoding='utf-8') as config:
            json.dump(self.data, config, indent=4)
