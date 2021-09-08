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

count = 0


def event(callback):
    global count
    count += 1
    print(f'{count}. Button press')


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(input_pin, GPIO.IN)
    print("Starting demo now! Press CTRL+c to exit")
    GPIO.add_event_detect(input_pin, GPIO.FALLING, callback=event, bouncetime=1000)

    try:
        while True:
            time.sleep(1)
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
