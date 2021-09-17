#!/usr/bin/python3
"""
    author: Jin-Mo, Lin
    email: s106003041@g.ksu.edu.tw
    description: jetson nano GPIO example button event
"""

import RPi.GPIO as GPIO
import time

# input_pin = 4       # BCM model with GPIO 4, BOARD model with Pin 7
input_pin = 18       # BCM model with GPIO 18, BOARD model with Pin 12
machine_output = 23

count = 0


def event(callback):
    global count
    global input_pin
    GPIO.cleanup(input_pin)
    count += 1
    print(f'{count}. Button press')
    GPIO.output(machine_output, GPIO.LOW)
    time.sleep(2)
    GPIO.output(machine_output, GPIO.HIGH)
    # for i in range(5):
    #     GPIO.output(machine_output, GPIO.HIGH)
        # print(f'{i+1}. thread')
        # time.sleep(2)
        # GPIO.output(machine_output, GPIO.LOW)

    GPIO.setup(input_pin, GPIO.IN)
    GPIO.add_event_detect(input_pin, GPIO.FALLING, callback=event, bouncetime=1000)



def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(input_pin, GPIO.IN)
    GPIO.setup(machine_output, GPIO.OUT, initial=GPIO.LOW)
    print("Starting demo now! Press CTRL+c to exit")
    GPIO.add_event_detect(input_pin, GPIO.FALLING, callback=event, bouncetime=1000)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
