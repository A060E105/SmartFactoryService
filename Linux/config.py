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

last_version = '2.8.0'


class Configuration:
    _instance = None
    filename = 'SmartFactory.conf'

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
            self.version = last_version
            self.save()
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
    def encoder_model_name(self) -> str:
        return self.data['encoder_model_name']

    @property
    def device_name(self) -> str:
        return self.data['device_name']

    @property
    def result_ratio(self) -> float:
        ratio = self.data.get('result_ratio', 50)
        if ratio > 100 or ratio <= 0:
            ratio = 100
        return ratio / 100

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
    def delay_time(self) -> int:
        return self.data.get('delay_time', 0)

    @property
    def backup_path(self) -> str:
        return self.data.get('backup_path', './backup')

    @property
    def is_ftp_backup(self) -> bool:
        return str(self.data.get('remote_system', '')).upper() == 'FTP'

    @property
    def remote_backup_path(self) -> str:
        return self.data.get('remote_backup_path', '')

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
    def picture_width(self) -> int:
        return self.data['spectrogram'].get('picture_width', 200)

    @property
    def picture_height(self) -> int:
        return self.data['spectrogram'].get('picture_height', 100)

    @property
    def freq_split_list(self) -> list:
        return self.data['spectrogram'].get('freq_split_list', [[0, 10000]])

    @property
    def binsize(self) -> 'int|None':
        return self.data['spectrogram'].get('binsize', None)

    @property
    def hopsize(self) -> int:
        return self.data['spectrogram'].get('hopsize', None)

    @property
    def with_cut_file(self) -> bool:
        return self.data['spectrogram']['with_cut_file']

    @property
    def save_split_audio(self) -> bool:
        return self.data['spectrogram']['save_split_audio']

    @property
    def vmin(self) -> int:
        return self.data['spectrogram'].get('vmin', -90)

    @property
    def vmax(self) -> int:
        return self.data['spectrogram'].get('vmax', 30)

    @property
    def KDE_score(self) -> int:
        return self.data['AI_analysis'].get('KDE_score', 8000)

    @property
    def MSE_score(self) -> float:
        return self.data['AI_analysis'].get('MSE_score', 0.047)

    @property
    def port(self) -> int:
        return self.data['server']['port']

    @property
    def ftp_server(self) -> str:
        return self.data['FTP'].get('server')

    @property
    def ftp_port(self) -> int:
        return self.data['FTP'].get('port')

    @property
    def ftp_username(self) -> str:
        return self.data['FTP'].get('username')

    @property
    def ftp_passwd(self) -> str:
        return self.data['FTP'].get('passwd')

    @property
    def ftp_path(self) -> str:
        return self.data['FTP'].get('path')

    @property
    def status_message(self) -> dict:
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
        self.data['version'] = last_version
        self.data['model_name'] = 'model.h5'
        self.data['encoder_model_name'] = 'encoder_model.h5'
        self.data['device_name'] = "A"
        self.data['result_ratio'] = 50
        # device settings
        self.data['device'] = {}
        self.data['device']['mic_default'] = {'name': 'Cotron EZM-001-2', 'calibration': 1}
        self.data['device']['mic_1'] = {'name': 'Cotron EZM-001-1', 'calibration': 1}
        self.data['device']['mic_2'] = {'name': 'Cotron EZM-001-2', 'calibration': 1}
        # before analysis the unit is second
        self.data['delay_time'] = 2
        # backup audio path
        self.data['backup_path'] = './backup'
        self.data['remote_system'] = ''
        # remote backup audio path
        self.data['remote_backup_path'] = ''
        # audio settings
        self.data['audio'] = {}
        self.data['audio']['second'] = 5
        self.data['audio']['framerate'] = 96000
        self.data['audio']['samples'] = 4096
        self.data['audio']['sampwidth'] = 2
        self.data['audio']['channels'] = 1
        # spectrogram settings
        self.data['spectrogram'] = {}
        self.data['spectrogram']['picture_width'] = 200
        self.data['spectrogram']['picture_height'] = 100
        self.data['spectrogram']['freq_split_list'] = [[0, 10000]]
        self.data['spectrogram']['binsize'] = 2 ** 10
        self.data['spectrogram']['hopsize'] = int((2 ** 10) * 0.5)
        self.data['spectrogram']['with_cut_file'] = True
        self.data['spectrogram']['save_split_audio'] = False
        self.data['spectrogram']['vmin'] = -90
        self.data['spectrogram']['vmax'] = 30
        # AI_analysis
        self.data['AI_analysis'] = {}
        self.data['AI_analysis']['KDE_score'] = 8000
        self.data['AI_analysis']['MSE_score'] = 0.047
        # server settings
        self.data['server'] = {}
        self.data['server']['port'] = 7000
        # FTP settings
        self.data['FTP'] = {}
        self.data['FTP']['server'] = '127.0.0.1'
        self.data['FTP']['username'] = 'username'
        self.data['FTP']['passwd'] = 'passwd'
        self.data['FTP']['port'] = 21
        self.data['FTP']['path'] = 'backup_path'
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
