"""
    Smart Factory
    audio class
    hello world
"""
import platform
import re
import os
import shutil
# from tensorflow.python.framework.ops import device
import time
import tqdm
import wave
import numpy as np
from pyaudio import PyAudio, paInt16
import soundfile
from pydub import AudioSegment      # wav to mp3
# A-weighting
from numpy import pi, polymul
from scipy.signal import bilinear, lfilter
# convert to specgram
import io
import cv2
from PIL import Image
from numpy.lib import stride_tricks
from matplotlib import pyplot as plt
# AI analysis
import glob
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
# thread
from threading import Thread, Lock
from multiprocessing import Process, Queue
from collections import namedtuple
# configuration
from config import Configuration
from storage import storage as STORAGE

from Logger import get_logger

# disable debugging logs
# 0 -> all info
# 1 -> info message not print
# 2 -> info and warning message not print
# 3 -> info, warning and error message not print
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'

plt.switch_backend('agg')   # 解決在非GUI環境下無法執行的問題
# =======================================================
#                   public variable 
# =======================================================
CONFIG = Configuration()
log = get_logger()
SOURCE_PATH = './source/'
AUDIO_OUT_PATH = './audio/'
SPEC_PATH = './spec/'

gpus = tf.config.list_physical_devices('GPU')
if gpus:
    # Restrict TensorFlow to only allocate 1GB of memory on the first GPU
    try:
        tf.config.set_logical_device_configuration(
            gpus[0],
            [tf.config.LogicalDeviceConfiguration(memory_limit=1024)])
    except RuntimeError as e:
        log.exception(e)

MODEL = load_model('./' + CONFIG.model_name)


# =======================================================
#                   public methods 
# =======================================================

def my_mkdir(path: str) -> None:
    now_path = ''
    for i in path.split('\\'):
        now_path = os.path.join(now_path, i)
        try:
            # os.mkdir(now_path)
            os.makedirs(now_path)
        except:
            pass


def wav_to_mp3(action=None, filename=None) -> None:
    # convert folder all wav file or convert one wav file
    if action == 'all':
        search = '*.wav'
    else:
        search = f'{filename}.wav'

    # using to source folder
    wav_files = glob.glob(SOURCE_PATH + search)
    for name in tqdm.tqdm(wav_files):
        file = name.split('/')[-1]
        filename = file.split('.')[0]
        # sound = AudioSegment.from_mp3(name)
        sound = AudioSegment.from_wav(name)
        sound.export(SOURCE_PATH + filename + '.mp3', format='mp3')


def rm_file(path='', filename=None) -> None:
    file = path + filename
    if os.path.exists(file):
        os.remove(file)


def backup(filename=None, result='') -> None:
    target = CONFIG.backup_path
    target = target.replace('\\', '/')
    file = SOURCE_PATH + filename

    # create NG/OK folder
    for folder in AI_analysis.my_class:
        path = os.path.join(target, STORAGE.filename, folder)
        my_mkdir(path)

    try:
        target_path = os.path.join(target, STORAGE.filename, result)
        shutil.move(file, target_path)
    except PermissionError:
        log.warning('Backup exception is Permission error')
        pass
    except:
        log.exception('Backup exception', exc_info=False)
        pass


def remote_backup(filename=None, result='') -> None:
    """
    備份至遠端目錄

    :param filename:
    :param result:
    :return:
    """
    target = CONFIG.remote_backup_path
    target = target.replace('\\', '/')
    if target != '':    # 路徑不為空才執行遠端備份
        file = SOURCE_PATH + filename

        # create NG/OK folder
        for folder in AI_analysis.my_class:
            path = os.path.join(target, STORAGE.filename, folder)
            my_mkdir(path)

        try:
            target_path = os.path.join(target, STORAGE.filename, result, filename)
            shutil.copyfile(file, target_path)
        except PermissionError:
            log.warning('Remote Backup exception is Permission error')
            pass
        except:
            log.exception('Remote Backup exception', exc_info=False)
            pass


def parser_result(results: list) -> str:
    ok_count = 0
    for item in results:
        # 計算 OK 的數量
        if item == 'OK':
            ok_count += 1

    # OK 的數量必須大於設定值
    if (ok_count / len(results)) > CONFIG.result_ratio:
        result = 'OK'
    else:
        result = 'NG'

    return result


# =============================================================================
#   Audio class
# =============================================================================
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
                for _ in tqdm.trange(int(self.framerate / self.samples * self.second), desc=f"record {self.filename}.wav"):
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
    
        NUMs = [(2*pi * f4)**2 * (10**(A1000/20)), 0, 0, 0, 0]
        DENs = polymul([1, 4*pi * f4, (2*pi * f4)**2],
                       [1, 4*pi * f1, (2*pi * f1)**2])
        DENs = polymul(polymul(DENs, [1, 2*pi * f3]),
                                     [1, 2*pi * f2])
    
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
        cali = np.sqrt(np.mean(np.absolute(source_data)**2))
        log.debug(f'cali: {cali}')
        db = 20*np.log10(np.sqrt(np.mean(np.absolute(self.source_record_data)**2))/(ref*cali))
        log.debug(f'db: {db}')
        AWcali = AW / cali
        self.record_data = AWcali.astype(np.short).tobytes()

    def get_calibration(self) -> float:
        """
        get calibration value
        """
        # source_data = np.frombuffer(self.record_data, dtype=np.short)
        # source_data = source_data / 32768
        # source_data = source_data / 16384
        ref = 0.00002
        cali_path = os.path.join(SOURCE_PATH, 'cali.wav')
        source_data, fs = soundfile.read(cali_path)
        b, a = self.__A_weighting(fs)
        AW_data = lfilter(b, a, source_data)
        cali = 0.2 / (np.sqrt(np.mean(np.absolute(AW_data)**2)))
        log.debug(f'cali: {cali}')
        db = 20*np.log10(np.sqrt(np.mean(np.absolute(AW_data)**2))/(ref*cali))
        log.debug(f'db: {db}')
        # CONFIG.set_cali(self.config_name, cali)
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
        # print("numdevices %s" %(numdevices))
        # print(f'connected devices: {self.getDeviceName()}')
        # print(f'configuration device name: {CONFIG.mic_default_name}')
        # print(f'self device name: {self.device}')
        for i in range(0, numdevices):
            if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                if ((re.search(device_name, p.get_device_info_by_host_api_device_index(0, i).get('name'))) is not None):
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


# =============================================================================
#       Specgram class
# =============================================================================
class Specgram:
    picture_width, picture_height = CONFIG.picture_width, CONFIG.picture_height
    CutTimeDef = 2
    SpaceNumDef = 1 
    freq_split_list = CONFIG.freq_split_list

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.with_cut_file = CONFIG.with_cut_file
        self.save_split_audio = CONFIG.save_split_audio

    def toSpecgram(self):
        my_mkdir(AUDIO_OUT_PATH)
        my_mkdir(SPEC_PATH)
        index = 0
        for audio_info, image_list in self.__CutFile():
            index += 1
            if self.save_split_audio:
                sampwidth = audio_info[0]
                framerate = audio_info[1]
                temp_dataTemp = audio_info[2]
                audio_file_name = '{}_{}.wav'.format(self.filename, index)
                audio_save_dir = os.path.join( AUDIO_OUT_PATH, self.filename)
                my_mkdir(audio_save_dir)
                audio_save_path = os.path.join(audio_save_dir, audio_file_name)
                f = wave.open(audio_save_path, "wb")
                f.setnchannels(1)
                f.setsampwidth(sampwidth)
                f.setframerate(framerate)

                f.writeframes(temp_dataTemp.tobytes())
                f.close()

            for freq_info, image in zip(self.freq_split_list, image_list):
                img_bin = Image.fromarray(image.astype(np.uint8), 'RGB')
                freq_str = '{}~{}'.format(freq_info[0], freq_info[1])
                image_dir = os.path.join(SPEC_PATH, freq_str, self.filename)
                file_name = '{}_{}.png'.format(self.filename, index)
                my_mkdir(image_dir)
                image_path = os.path.join(image_dir, file_name)
                img_bin.save(image_path)

    @property
    def file_path(self) -> str:
        return f"{SOURCE_PATH}{self.filename}.wav"

    def __CutFile(self) -> list:
        f = wave.open( self.file_path , "rb")
        params = f.getparams()
        
        nchannels, sampwidth, framerate, nframes = params[:4]
        CutFrameNum = framerate * self.CutTimeDef
        str_data = f.readframes(nframes)
        f.close()
        wave_data = np.frombuffer(str_data, dtype=np.short)

        if nchannels >= 2:  
            wave_data.shape = -1, 2
            wave_data = wave_data.T
        else:
            wave_data = wave_data.reshape(1, wave_data.shape[0])

        if self.with_cut_file:
            ptr_start = 0
            time = 0
            total_time = (wave_data.shape[1] / framerate / self.SpaceNumDef) - self.CutTimeDef 
            total_time = int(total_time) + 1
            with tqdm.tqdm(total=total_time, desc=f"{self.filename}.wav to specgram") as pbar:
                while 1:
                    ptr_end = ptr_start + self.CutTimeDef * framerate
                    ptr_end = int(ptr_end)
                    if ptr_end <= nframes:
                        temp_dataTemp = wave_data[0][ptr_start:ptr_end]  
                        image_list = self.__plotstft(self.freq_split_list, self.picture_width, self.picture_height,
                                                     framerate, temp_dataTemp)
                        ptr_start += self.SpaceNumDef * framerate
                        ptr_start = int(ptr_start)
                        time += 1
                        pbar.update(1)
                        #print('\n' , ptr_start , ptr_end, '\n')
                        yield [sampwidth, framerate, temp_dataTemp], image_list
                    else:
                        break
        else:
            temp_dataTemp = wave_data[0]
            image_list = self.__plotstft(self.freq_split_list, self.picture_width, self.picture_height, framerate,
                                         temp_dataTemp)
            yield [sampwidth, framerate, temp_dataTemp], image_list

    def __plotstft(self, freq_split_list, im_width, im_height, samplerate, samples, binsize=2**10, plotpath=None, colormap="jet") -> np:
        if CONFIG.binsize is not None:
            binsize = CONFIG.binsize
        s = self.__stft(samples, binsize)
        sshow_origin, freq = self.__logscale_spec(s, factor=1.0, sr=samplerate)
        image_list = []
        for f_split in freq_split_list:
            freq = np.array(freq)
            mask = (freq >= f_split[0] ) * (freq < f_split[1] ) 
            index_list = [ index for index,x in enumerate(mask) if x]  
            sshow = sshow_origin[ : , index_list]
            
            # ims = 20.*np.log10(np.abs(sshow)/10e-6) # amplitude to decibel
            ims = 20. * np.log10(np.abs(sshow) / 10e+6)  #dBFS
            # ims = 20.*np.log10(np.abs(sshow)/10e-3)
            # ims = 20.*np.log10(np.abs(sshow)/32768)
            # ims = 20*np.log10(np.abs(sshow)/32768)
            # ims = np.abs(sshow) 

            # timebins, freqbins = np.shape(ims)
            #print("timebins: ", timebins)
            #print("freqbins: ", freqbins)
            # plt.imshow(np.transpose(ims), origin="None", aspect="auto", cmap="jet", extent = None, interpolation='None', vmin= -160, vmax= 0)
            plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap="jet", extent = None, interpolation='None', vmin= -160, vmax= 0)
            plt.axis('off') 
            fig = plt.gcf()
            fig.set_size_inches(  im_width , im_height  ) #dpi = 300, output = 700*700 pixels
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
            plt.margins(0,0)

            img_arr = self.__get_img_from_fig( fig , dpi = 1 )
            image_list.append( img_arr )
            plt.clf()
        return np.array(image_list)

    def __logscale_spec(self, spec, sr=96000, factor=20.) -> tuple:
        timebins, freqbins = np.shape(spec)
    
        scale = np.linspace(0, 1, freqbins) ** factor
        scale *= (freqbins-1)/max(scale)
        scale = np.unique(np.round(scale))
    
        # create spectrogram with new freq bins
        newspec = np.complex128(np.zeros([timebins, len(scale)]))
        for i in range(0, len(scale)):        
            if i == len(scale)-1:
                newspec[:,i] = np.sum(spec[:,int(scale[i]):], axis=1)
            else:        
                newspec[:,i] = np.sum(spec[:,int(scale[i]):int(scale[i+1])], axis=1)
    
        # list center freq of bins
        allfreqs = np.abs(np.fft.fftfreq(freqbins*2, 1./sr)[:freqbins+1])
        freqs = []
        for i in range(0, len(scale)):
            if i == len(scale)-1:
                freqs += [np.mean(allfreqs[int(scale[i]):])]
            else:
                freqs += [np.mean(allfreqs[int(scale[i]):int(scale[i+1])])]
    
        return newspec, freqs

    def __stft(self, sig, frameSize, overlapFac=0.5, window=np.hanning) -> np:
        win = window(frameSize)
        hopSize = int(frameSize - np.floor(overlapFac * frameSize))
        # zeros at beginning (thus center of 1st window should be for sample nr. 0)   
        samples = np.append(np.zeros(int(np.floor(frameSize/2.0))), sig)    
        # cols for windowing
        cols = np.ceil( (len(samples) - frameSize) / float(hopSize)) + 1
        # zeros at end (thus samples can be fully covered by frames)
        samples = np.append(samples, np.zeros(frameSize))
        
        frames = stride_tricks.as_strided(samples, shape=(int(cols), frameSize), strides=(samples.strides[0]*hopSize, samples.strides[0])).copy()
        frames *= win
        return np.fft.rfft(frames)    

    def __get_img_from_fig(self, fig, dpi=180) -> cv2:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi)
        buf.seek(0)
        img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
        buf.close()
        img = cv2.imdecode(img_arr, 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img


# =============================================================================
#   AI analysis class
# =============================================================================
class AI_analysis():
    resize_shape = ( 100, 200 )
    batch_size = 32
    my_class = ['NG', 'OK']

    def __init__(self, filename) -> None:
        self.filename = filename
        self.model = MODEL
        self.analysis = []

    def __getResult(self) -> list:
        file_path = os.path.join('spec', '0~10000', 'demo')
        f_names = glob.glob(file_path + '/*.png')


        img = []
        for i in range(len(f_names)):
            images = image.load_img(f_names[i], target_size=(100, 200))
            x = image.img_to_array(images)
            x = np.expand_dims(x, axis=0)
            img.append(x)

        x = np.concatenate([x for x in img])
        y = self.model.predict(x)

        return []

    def getResult(self) -> list:
        file_path = os.path.join('spec', '0~10000', self.filename)
        f_names = glob.glob(file_path + '/*.png')

        img = []
        for i in range(len(f_names)):
            images = image.load_img(f_names[i], target_size=(100, 200))
            x = image.img_to_array(images)
            x = np.expand_dims(x, axis=0)
            img.append(x)


        x = np.concatenate([x for x in img])

        # self.model.summary()
        y = self.model.predict(x)

        for predict in y:
            predict_class = self.my_class[ np.argmax(predict)]
            self.analysis.append(predict_class)

        return self.analysis

    # def getResult(self) -> list:
    #     return self.analysis


# =============================================================================
#    Smart Factory Service
# =============================================================================
class SmartFactoryService:
    Result = namedtuple('Result', ['status', 'model', 'result'])

    def __init__(self, filename='', device='', queue=None, gpu_lock=None, config=None) -> None:
        self.filename = filename
        self.queue = queue
        self.gpu_lock = gpu_lock
        self.device = 'Cotron EZM-001'
        self.config_name = config
        self.au = Audio(self.filename, device=self.device, config=config)

    # action all, record -> to spectrogram -> AI analysis
    def all(self) -> None:
        # print(*self.au.getDeviceName(), sep = ", ")
        # print(self.au.getDeviceName())
        try:
            if self.au.hasDevice():
                self.au.record()
                self.au.A_weighting()
                self.au.save_wav()
                my_thread = Thread(self.comb_spec_AI(self.filename, gpu_lock=self.gpu_lock, queue=self.queue))
                my_thread.start()
                my_thread.join()
                analysis_result = self.queue.get()
                self.queue.put(analysis_result)
                wav_to_mp3(filename=self.filename)
                # rm_file(path=SOURCE_PATH, filename=self.filename + '.wav')
                remote_backup(filename=self.filename + '.mp3', result=analysis_result.get('result')[0])
                backup(filename=self.filename + '.mp3', result=analysis_result.get('result')[0])
            else:
                # result = ["has not found device", "please check your device"]
                # result = {
                #     'status': 2,
                #     'result': []
                # }
                result = dict(self.Result(status=2, model=[], result=[])._asdict())
                self.queue.put(result)
        except Exception as exc:
            log.exception(f'SmartFactoryService all exception: {str(exc)}')
            # result = {
            #     'status': 2,
            #     'result': []
            # }
            result = dict(self.Result(status=2, model=[], result=[])._asdict())
            self.queue.put(result)

    # action two, only record
    def rec_only(self) -> None:
        if self.au.hasDevice():
            self.au.record()
            self.au.A_weighting()
            self.au.save_wav()
            result = ["Success"]
        else:
            result = ["has not found device", "please check your device"]
        self.queue.put(result)

    # action spectrogram only
    def spec_only(self) -> None:
        self.gpu_lock.acquire()
        file_path = f'{SOURCE_PATH}{self.filename}.wav'
        result = []
        try:
            if os.path.exists(file_path):
                Specgram(filename=self.filename).toSpecgram()
                result = ['success', 'to spectrogram']
            else:
                result = ['not found file']
        finally:
            self.queue.put(result)
            self.gpu_lock.release()

    # action three, to spectrogram -> AI analysis
    def spec_ai(self) -> None:
        file_path = f'{SOURCE_PATH}{self.filename}.wav'
        if os.path.exists(file_path):
            my_thread = Thread(self.comb_spec_AI(self.filename, gpu_lock=self.gpu_lock, queue=self.queue))
            my_thread.start()
            my_thread.join()
        else:
            result = ['Error', 'not found file']
            self.queue.put(result)

    # action boot_init
    def boot_init(self) -> None:
        boot_au = Audio("boot_init", device=self.device, second=5)
        if boot_au.hasDevice():
            boot_au.record()    # first record with error
            time.sleep(5)       # delay 5 second
            boot_au.record()    # record again
            boot_au.save_wav()
            my_thread = Thread(self.comb_spec_AI("boot_init", gpu_lock=self.gpu_lock, queue=self.queue))
            my_thread.start()
            my_thread.join()
            self.rm_init_file()     # remove boot initialize file
        else:
            result = ["has not found device", "please check your device"]
            self.queue.put(result)

    def comb_spec_AI(self, filename, gpu_lock, queue) -> None:
        gpu_lock.acquire()
        try:
            Specgram(filename).toSpecgram()
            # result = AI_analysis(filename).getResult()
            # result = {
            #     'status': 0,
            #     'result': AI_analysis(filename).getResult()
            # }
            response = AI_analysis(filename).getResult()
            response = parser_result(response)
            result = dict(self.Result(status=0, model=[CONFIG.model_name], result=[response])._asdict())
            queue.put(result)
        finally:
            gpu_lock.release()

    def auto_cali(self) -> None:
        """
        microphone calibration and save value to config
        """
        cali_au = Audio('cali', device=self.device, second=5)
        if cali_au.hasDevice():
            cali_au.record()
            cali_au.save_wav()
            CONFIG.set_cali(self.config_name, cali_au.get_calibration())
            rm_file(path=SOURCE_PATH, filename='cali.wav')
            result = dict(self.Result(status=0, model=[], result=['Success'])._asdict())
            self.queue.put(result)
        else:
            result = dict(self.Result(status=2, model=[], result=[])._asdict())
            self.queue.put(result)

    def get_cali(self) -> None:
        """
        get microphone calibration value
        """
        cali_au = Audio('cali', device=self.device, second=5)
        if cali_au.hasDevice():
            cali_au.record()
            cali_au.save_wav()
            cali = cali_au.get_calibration()
            rm_file(path=SOURCE_PATH, filename='cali.wav')
            result = dict(self.Result(status=0, model=[], result=[CONFIG.get_cali(self.config_name), cali])._asdict())
            self.queue.put(result)
        else:
            result = dict(self.Result(status=2, model=[], result=[])._asdict())
            self.queue.put(result)

    def set_cali(self, value) -> None:
        """
        set microphone calibration value save to config
        """
        CONFIG.set_cali(self.config_name, value)
        result = dict(self.Result(status=0, model=[], result=['Save Success'])._asdict())
        self.queue.put(result)

    def rm_init_file(self) -> None:
        boot_init_filename = 'boot_init'
        source_file = SOURCE_PATH + boot_init_filename + '.wav'
        audio_path = os.path.join(AUDIO_OUT_PATH, boot_init_filename)
        spec_path = os.path.join(SPEC_PATH, '0~10000', boot_init_filename)

        if os.path.exists(source_file):
            os.remove(source_file)

        try:
            shutil.rmtree(spec_path)    # first remove spec
            shutil.rmtree(audio_path)
        except OSError:
            pass


# if __name__ == '__main__':
#     filename = 'demo'
#     model_file = './model.h5'
#     queue = Queue()
#     sfs = SmartFactoryService(filename, device=Audio.DEVICE_1, model=model_file, queue=queue)
#     sfs.run()
#     print('main', queue.get())
#
