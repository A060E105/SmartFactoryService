import abc
import platform

if platform.system() == 'Linux':
    import RPi.GPIO as GPIO

import serial
import time
from pynput.keyboard import Key, Listener


class __IOCtrlAbstract(abc.ABC):

    @abc.abstractmethod
    def machine_down(self):
        return NotImplemented

    @abc.abstractmethod
    def machine_up(self):
        return NotImplemented

    @abc.abstractmethod
    def wait_machine_response(self):
        return NotImplemented

    @abc.abstractmethod
    def enable(self):
        return NotImplemented

    @abc.abstractmethod
    def disable(self):
        return NotImplemented

    @abc.abstractmethod
    def cleanup(self):
        return NotImplemented


class SerialIO(__IOCtrlAbstract):
    def __init__(self, port: str, baud_rate: int) -> None:
        self.__port = port
        self.__baud_rate = baud_rate

    def machine_down(self):
        print('Serial 汽缸下壓')

    def machine_up(self):
        print('Serial 汽缸上升')

    def wait_machine_response(self):
        print('Serial 等待汽缸回傳')

    def enable(self):
        pass

    def disable(self):
        pass

    def cleanup(self):
        pass


if platform.system() == 'Linux':
    class MyGPIO(__IOCtrlAbstract):
        def __init__(self, start_pin: int, machine_tx: int, machine_rx: int) -> None:
            self.__start_pin = start_pin
            self.__machine_tx = machine_tx
            self.__machine_rx = machine_rx
            self.__instance = None
            self.__enable_callback = None
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.__start_pin, GPIO.IN)
            GPIO.setup(self.__machine_rx, GPIO.IN)
            GPIO.setup(self.__machine_tx, GPIO.OUT, initial=GPIO.LOW)

        def set_callback(self, instance):
            self.__instance = instance
            self.enable()

        def machine_down(self):
            print('GPIO 汽缸下壓')
            GPIO.output(self.__machine_tx, GPIO.HIGH)

        def machine_up(self):
            print('GPIO 汽缸上升')
            GPIO.output(self.__machine_tx, GPIO.LOW)

        def wait_machine_response(self):
            print('GPIO 等待汽缸回傳')
            while GPIO.input(self.__machine_rx):
                pass

        def enable(self):
            print('GPIO enable start button')
            GPIO.add_event_detect(self.__start_pin, GPIO.FALLING, callback=self.__instance, bouncetime=5000)

        def disable(self):
            print('GPIO disable start button')
            GPIO.remove_event_detect(self.__start_pin)
            pass

        def cleanup(self):
            GPIO.cleanup()
            print('GPIO cleanup')


class VirtualIO(__IOCtrlAbstract):
    def __init__(self) -> None:
        self.__listener = None
        self.__callback = None

    def set_callback(self, callback):
        self.__callback = callback
        self.enable()

    def machine_down(self):
        print('Virtual I/O 汽缸下壓')

    def machine_up(self):
        print('Virtual I/O 汽缸上升')

    def wait_machine_response(self):
        print('Virtual I/O 等待汽缸回傳')
        time.sleep(2)

    def enable(self):
        print('Virtual I/O 啟用按鈕')

        def on_press(key):
            if key == Key.space:
                print('按下space開始分析')
                self.__callback('')
                return False
            print(f'按下了{key}鍵')

        def on_release(key):
            print(f'鬆開了{key}鍵')

        self.__listener = Listener(on_press=on_press, on_release=on_release)
        self.__listener.start()
        # with Listener(on_press=on_press, on_release=on_release) as listener:
        #     print('Virtual I/O 啟用按鈕 2')
        #     listener.join()

        print('Virtual I/O 啟用按鈕 3')

    def disable(self):
        print('Virtual I/O 禁用按鈕')

    def cleanup(self):
        print('Virtual I/O cleanup')
        self.__listener.stop()


class IOCtrl(__IOCtrlAbstract):
    def __init__(self, instance: 'MyGPIO | SerialIO | VirtualIO') -> None:
        self.__instance = instance

    def machine_down(self):
        self.__instance.machine_down()

    def machine_up(self):
        self.__instance.machine_up()

    def wait_machine_response(self):
        self.__instance.wait_machine_response()

    def enable(self):
        self.__instance.enable()

    def disable(self):
        self.__instance.disable()

    def cleanup(self):
        self.__instance.cleanup()


# ==============================================================================
# ------------------------------------ END -------------------------------------
# ==============================================================================
