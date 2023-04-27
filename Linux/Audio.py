import re
import os
import tqdm
import wave
import soundfile
import numpy as np
from pyaudio import PyAudio, paInt16
from numpy import pi, polymul
from scipy.signal import bilinear, lfilter

from Logger import get_logger
from config import Configuration

CONFIG = Configuration()
log = get_logger()
SOURCE_PATH = './source/'


def my_mkdir(path: str) -> None:
    now_path = ''
    for i in path.split('\\'):
        now_path = os.path.join(now_path, i)
        try:
            os.makedirs(now_path)
        except:
            pass


class Audio:
    DEVICE_DEFAULT = CONFIG.mic_default_name
    DEVICE_1 = CONFIG.mic_1_name
    DEVICE_2 = CONFIG.mic_2_name

    DEFAULT_CALI = CONFIG.mic_default_cali
    MIC_1_CALI = CONFIG.mic_1_cali
    MIC_2_CALI = CONFIG.mic_2_cali

    DEFAULT = 'mic_default'
    MIC_1 = 'mic_1'
    MIC_2 = 'mic_2'

    framerate = CONFIG.framerate
    samples = CONFIG.samples
    sampwidth = CONFIG.sampwidth
    channels = CONFIG.channels

    def __init__(self, filename, device='', second=CONFIG.second, config=DEFAULT) -> None:
        self.filename = filename
        self.record_data = b''
        self.device = device
        self.second = second + 0.5
        self.source_record_data = None
        self.config_name = config

    def record(self) -> None:
        if self.hasDevice():
            try:
                pa = PyAudio()
                stream = pa.open(format=paInt16,
                                 channels=self.channels,
                                 rate=self.framerate,
                                 input=True,
                                 input_device_index=self.__getDevice(self.device),
                                 frames_per_buffer=self.samples)
                my_buf = []
                for _ in tqdm.trange(int(self.framerate / self.samples * self.second),
                                     desc=f"record {self.filename}.wav"):
                    string_audio_data = stream.read(self.samples, exception_on_overflow=False)
                    my_buf.append(string_audio_data)
                stream.stop_stream()
                stream.close()
                pa.terminate()
                self.record_data = np.array(my_buf).tobytes()
                self.source_record_data = np.array(my_buf).tobytes()
            except:
                pass

    def save_wav(self) -> None:
        my_mkdir(SOURCE_PATH)
        wf = wave.open(f"{SOURCE_PATH}{self.filename}.wav", 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sampwidth)
        wf.setframerate(self.framerate)
        wf.writeframes(self.record_data)
        wf.close()

    def A_weighting(self) -> None:
        f1 = 20.598997
        f2 = 107.65265
        f3 = 737.86223
        f4 = 12194.217
        A1000 = 1.9997

        NUMs = [(2 * pi * f4) ** 2 * (10 ** (A1000 / 20)), 0, 0, 0, 0]
        DENs = polymul([1, 4 * pi * f4, (2 * pi * f4) ** 2],
                       [1, 4 * pi * f1, (2 * pi * f1) ** 2])
        DENs = polymul(polymul(DENs, [1, 2 * pi * f3]),
                       [1, 2 * pi * f2])

        # Use the bilinear transformation to get the digital filter.
        # (Octave, MATLAB, and PyLab disagree about Fs vs 1/Fs)
        b, a = bilinear(NUMs, DENs, self.framerate)

        data = np.frombuffer(self.record_data, dtype=np.short)
        AW = lfilter(b, a, data)

        CONFIG.read()
        cali = CONFIG.get_cali(self.config_name)
        AWcali = AW * float(cali)

        self.record_data = AWcali.astype(np.short).tobytes()

    def __A_weighting(self, fs):
        f1 = 20.598997
        f2 = 107.65265
        f3 = 737.86223
        f4 = 12194.217
        A1000 = 1.9997

        NUMs = [(2 * pi * f4) ** 2 * (10 ** (A1000 / 20)), 0, 0, 0, 0]
        DENs = polymul([1, 4 * pi * f4, (2 * pi * f4) ** 2],
                       [1, 4 * pi * f1, (2 * pi * f1) ** 2])
        DENs = polymul(polymul(DENs, [1, 2 * pi * f3]),
                       [1, 2 * pi * f2])

        # Use the bilinear transformation to get the digital filter.
        # (Octave, MATLAB, and PyLab disagree about Fs vs 1/Fs)
        return bilinear(NUMs, DENs, fs)

    def __calibration(self) -> None:
        ref = 0.00002
        source_data = np.frombuffer(self.source_record_data, dtype=np.short)
        AW = np.frombuffer(self.record_data, dtype=np.short)
        cali = np.sqrt(np.mean(np.absolute(source_data) ** 2))
        log.debug(f'cali: {cali}')
        db = 20 * np.log10(np.sqrt(np.mean(np.absolute(self.source_record_data) ** 2)) / (ref * cali))
        log.debug(f'db: {db}')
        AWcali = AW / cali
        self.record_data = AWcali.astype(np.short).tobytes()

    def get_calibration(self) -> float:
        """
        get calibration value
        """
        ref = 0.00002
        cali_path = os.path.join(SOURCE_PATH, 'cali.wav')
        source_data, fs = soundfile.read(cali_path)
        b, a = self.__A_weighting(fs)
        AW_data = lfilter(b, a, source_data)
        cali = 0.1 / (np.sqrt(np.mean(np.absolute(AW_data) ** 2)))
        # 202302116 , 0.2 -> 0.1  for 80dB ->74dB
        log.debug(f'cali: {cali}')
        db = 20 * np.log10(np.sqrt(np.mean(np.absolute(AW_data) ** 2)) / (ref * cali))
        log.debug(f'db: {db}')
        return cali

    def getDeviceName(self) -> list:
        p = PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        device_name_list = []
        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                device_name_list.append(p.get_device_info_by_host_api_device_index(0, i).get('name'))

        return device_name_list

    def __getDevice(self, device_name) -> "int | None":
        p = PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                if re.search(device_name, p.get_device_info_by_host_api_device_index(0, i).get('name')) is not None:
                    return i

    def hasDevice(self) -> bool:
        # develop test
        if self.device == 'test':
            return True

        if self.__getDevice(self.device) is None:
            log.warning("has not device")
            return False
        else:
            log.debug("has device")
            return True

    def get_decibel(self) -> float:
        y, sr = soundfile.read(f"{SOURCE_PATH}{self.filename}.wav")
        ref = 0.00002
        return 20 * np.log10(np.sqrt(np.mean(np.absolute(y) ** 2)) / ref)
