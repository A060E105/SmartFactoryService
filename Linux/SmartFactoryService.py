"""
    Smart Factory
    audio class
    hello world
"""
import platform
import re
import os
import shutil
from ftplib import FTP
import time
import tqdm
import wave
import numpy as np
import pandas as pd
import datetime
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
import pickle
import tensorflow as tf
from sklearn.neighbors import KernelDensity
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
# thread
from threading import Thread, Lock
from multiprocessing import Process, Queue
from collections import namedtuple
# configuration
from Audio import Audio
from config import Configuration
from storage import storage as STORAGE

from Logger import get_logger

import PyOctaveBand
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
FREQ_CSV_PATH = './freq_csv/'

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
ENCODER_MODEL = load_model('./' + CONFIG.encoder_model_name)


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
        sound = AudioSegment.from_wav(name)
        sound.export(SOURCE_PATH + filename + '.mp3', format='mp3')


def mp3_to_wav(filename=None) -> None:
    source_path = f"{SOURCE_PATH}{filename}.mp3"
    target_path = f"{SOURCE_PATH}{filename}.wav"
    cmd = f"ffmpeg -i {source_path} -vn -acodec pcm_s16le -f s16le -ac 1 -ar 96000 -f wav {target_path} -y"
    os.system(cmd)
    y, sr = soundfile.read(target_path)
    soundfile.write(target_path, y, sr, 'PCM_16')


def wav_to_csv(filename=None) -> None:
    my_mkdir(FREQ_CSV_PATH)
    fraction = 12
    limits = [100, 5000]
    source_path = f"{SOURCE_PATH}{filename}.wav"
    y, fs = soundfile.read(source_path)
    spectrum, freq_bands = PyOctaveBand.octavefilter(y, fs, fraction=fraction, limits=limits)
    df = pd.DataFrame({'freq': freq_bands, 'db': spectrum})
    df.to_csv(os.path.join(FREQ_CSV_PATH, f"{filename}.csv"))


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


def ftp_upload(filename=None, result=''):
    ftp_server = CONFIG.ftp_server
    ftp_username = CONFIG.ftp_username
    ftp_passwd = CONFIG.ftp_passwd
    ftp_port = CONFIG.ftp_port
    ftp_path = CONFIG.ftp_path

    ftp = FTP()
    ftp.connect(host=ftp_server, port=ftp_port)

    file = SOURCE_PATH + filename
    try:
        ftp.login(ftp_username, ftp_passwd)
        ftp.cwd(ftp_path)

        folder_name = datetime.datetime.now().strftime("%Y%m%d")
        if folder_name not in ftp.nlst():
            ftp.mkd(folder_name)

        ftp.cwd(folder_name)

        # create NG/OK folder
        # for folder in AI_analysis.my_class:
        #     if folder not in ftp.nlst():
        #         ftp.mkd(folder)
        #
        # ftp.cwd(result)
        ftp.storbinary(f"STOR {filename}", open(file, 'rb'), 1024)
        ftp.quit()
    except Exception as e:
        log.exception('Remote Backup exception from FTP.', exc_info=False)


def remote_backup(filename=None, result='') -> None:
    """
    備份至遠端目錄

    :param filename:
    :param result:
    :return:
    """
    if CONFIG.is_ftp_backup:
        ftp_upload(filename, result)
    else:
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
            mask = (freq >= f_split[0]) * (freq < f_split[1])
            index_list = [index for index, x in enumerate(mask) if x]
            sshow = sshow_origin[:, index_list]
            
            ims = 20. * np.log10(np.abs(sshow) / 10e+6)  # dBFS
            plt.imshow(np.transpose(ims), origin="lower", aspect="auto", cmap="jet", extent=None,
                       interpolation='None', vmin=CONFIG.vmin, vmax=CONFIG.vmax)
            plt.axis('off') 
            fig = plt.gcf()
            plt.yscale('symlog', linthresh=200)
            fig.set_size_inches(im_width, im_height)  # dpi = 300, output = 700*700 pixels
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
            plt.margins(0, 0)

            img_arr = self.__get_img_from_fig(fig, dpi=1)
            image_list.append(img_arr)
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
                newspec[:, i] = np.sum(spec[:, int(scale[i]):], axis=1)
            else:        
                newspec[:, i] = np.sum(spec[:, int(scale[i]):int(scale[i+1])], axis=1)
    
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
        if CONFIG.hopsize is not None:
            hopSize = CONFIG.hopsize
        else:
            hopSize = int(frameSize - np.floor(overlapFac * frameSize))
        # zeros at beginning (thus center of 1st window should be for sample nr. 0)   
        samples = np.append(np.zeros(int(np.floor(frameSize/2.0))), sig)    
        # cols for windowing
        cols = np.ceil((len(samples) - frameSize) / float(hopSize)) + 1
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
        self.encoder_model = ENCODER_MODEL

        with open('encoded_images_vector', 'rb') as fp:
            encoded_images_vector = pickle.load(fp)
            self.kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(encoded_images_vector)

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

    def getResult(self) -> tuple:
        target_dir = '~'.join(list(map(lambda x: str(x), CONFIG.freq_split_list[0])))
        file_path = os.path.join('spec', target_dir, self.filename)
        f_names = glob.glob(file_path + '/*.png')
        analysis_list = []

        for i in range(len(f_names)):
            analysis_list.append(self.get_analysis_result(f_names[i]))

        df = pd.DataFrame(analysis_list, columns=['density', 'thresholds'])
        density = round(df['density'].mean(), 6)
        thresholds = round(df['thresholds'].mean(), 6)

        if density < CONFIG.KDE_score or thresholds > CONFIG.MSE_score:
            analysis_result = 'NG'
        else:
            analysis_result = 'OK'

        return analysis_result, density, thresholds

    def get_analysis_result(self, img_path) -> tuple:
        encoder_output_shape = self.encoder_model.output_shape  # Here, we have 16x16x16
        out_vector_shape = encoder_output_shape[1] * encoder_output_shape[2] * encoder_output_shape[3]

        img = Image.open(img_path)
        img = np.array(img.resize((256, 256), Image.ANTIALIAS))
        # plt.imshow(img)
        img = img / 255.
        img = img[np.newaxis, :, :, :]
        # out_vector_shape=12544
        encoded_img = self.encoder_model.predict([[img]])
        encoded_img = [np.reshape(img, out_vector_shape) for img in encoded_img]
        density = self.kde.score_samples(encoded_img)[0]

        reconstruction = self.model.predict([[img]])
        reconstruction_error = self.model.evaluate([reconstruction], [[img]], batch_size=1)[0]
        # reconstruction_accuracy = self.model.evaluate([reconstruction], [[img]], batch_size=1)[1]

        return density, reconstruction_error

    def _old_backup_getResult(self) -> list:
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

    def __init__(self, filename='', device='Cotron EZM-001', queue=None, gpu_lock=None, config=None) -> None:
        self.filename = filename
        self.queue = queue
        self.gpu_lock = gpu_lock
        self.device = device
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
                wav_to_mp3(filename=self.filename)
                mp3_to_wav(filename=self.filename)
                wav_to_csv(filename=self.filename)  # wav to freq csv
                my_thread = Thread(self.combine_spec_ai(self.filename, gpu_lock=self.gpu_lock, queue=self.queue))
                my_thread.start()
                my_thread.join()
                self.combine_result()
                analysis_result = self.queue.get()
                self.queue.put(analysis_result)
                shutil.copyfile(os.path.join(SOURCE_PATH, f"{self.filename}.mp3"),
                                os.path.join(SOURCE_PATH, 'last_audio.mp3'))
                rm_file(path=SOURCE_PATH, filename=self.filename + '.wav')
                remote_backup(filename=self.filename + '.mp3', result=analysis_result.get('result')[0])
                backup(filename=self.filename + '.mp3', result=analysis_result.get('result')[0])
            else:
                result = dict(self.Result(status=2, model=[], result=[])._asdict())
                self.queue.put(result)
        except Exception as exc:
            log.exception(f'SmartFactoryService all exception: {str(exc)}')
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
            my_thread = Thread(self.combine_spec_ai(self.filename, gpu_lock=self.gpu_lock, queue=self.queue))
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
            my_thread = Thread(self.combine_spec_ai("boot_init", gpu_lock=self.gpu_lock, queue=self.queue))
            my_thread.start()
            my_thread.join()
            self.rm_init_file()     # remove boot initialize file
        else:
            result = ["has not found device", "please check your device"]
            self.queue.put(result)

    @staticmethod
    def __map_score_value(x, forty=8000.0, good=9000.0, isKDE=1):
        ratio = (good - forty) / 40
        if x > good:
            rvalue = 0
        else:
            rvalue = int((good - x) / ratio)

        return 100 if rvalue > 100 else rvalue

    @staticmethod
    def __map_value_MSE(x, forty, good):
        print(f"x={x}, zone={good}, forty={forty}")
        rvalue = ((x - good) / (forty - good)) * 40
        print(f"step1 rvalue={rvalue}")
        rvalue = 100 if rvalue > 100 else rvalue
        rvalue = 0 if rvalue < 0 else rvalue
        return rvalue

    def __get_ai_score1(self, kde):
        return self.__map_value_MSE(kde, CONFIG.forty_KDE_score, CONFIG.zero_KDE_score)

    def __get_ai_score2(self, mse):
        return self.__map_value_MSE(mse, CONFIG.forty_MSE_score, CONFIG.zero_MSE_score)

    def __get_freq_analysis(self):
        std_df = pd.read_csv('freq_ana.csv')
        test_df = pd.read_csv(os.path.join(FREQ_CSV_PATH, f"{self.filename}.csv"))
        result_df = std_df[std_df.db < test_df.db]
        return 'OK' if result_df.empty else 'NG'

    @staticmethod
    def __get_final_result(result1, result2):
        return 'FAIL' if 'NG' in [result1, result2] else 'PASS'

    def combine_result(self):
        data = self.queue.get()
        data['dB'] = self.au.get_decibel()
        data['ai_score1'] = self.__get_ai_score1(data.get('KDE_score')[0])
        data['ai_score2'] = self.__get_ai_score2(data.get('MSE_score')[0])
        data['freq_result'] = self.__get_freq_analysis()
        data['ai_result'] = data.get('result')[0]
        data['final_result'] = self.__get_final_result(data['freq_result'], data['ai_result'])
        self.queue.put(data)

    def combine_spec_ai(self, filename, gpu_lock, queue) -> None:
        gpu_lock.acquire()
        try:
            Specgram(filename).toSpecgram()

            response, density, thresholds = AI_analysis(filename).getResult()
            result = dict(self.Result(status=0, model=[CONFIG.model_name], result=[response])._asdict())
            result['KDE_score'] = [density]
            result['MSE_score'] = [thresholds]

            print(f"{result}")
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

    @staticmethod
    def rm_init_file() -> None:
        boot_init_filename = 'boot_init'
        source_file = SOURCE_PATH + boot_init_filename + '.wav'
        audio_path = os.path.join(AUDIO_OUT_PATH, boot_init_filename)
        target_dir = '~'.join(list(map(lambda x: str(x), CONFIG.freq_split_list[0])))
        spec_path = os.path.join(SPEC_PATH, target_dir, boot_init_filename)

        if os.path.exists(source_file):
            os.remove(source_file)

        try:
            shutil.rmtree(spec_path)    # first remove spec
            shutil.rmtree(audio_path)
        except OSError:
            pass
