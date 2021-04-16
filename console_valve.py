# console application for raspbery pi3 

import RPi.GPIO as GPIO
import sys


GPIO.setmode(GPIO.BCM)


# pin inicialization
pin_valve_one = 2
pin_valve_two = 3
pin_valve_three = 4
pin_valve_for = 5

# GPIO pin inicialization as OUT
GPIO.setup(pin_valve_one, GPIO.OUT)
GPIO.setup(pin_valve_two, GPIO.OUT)
GPIO.setup(pin_valve_three, GPIO.OUT)
GPIO.setup(pin_valve_for, GPIO.OUT)

# OUT inicialization as PWM object
valve_one = GPIO.PWM(pin_valve_one, 1)
valve_two = GPIO.PWM(pin_valve_two, 1)
valve_three = GPIO.PWM(pin_valve_three, 1)
valve_for = GPIO.PWM(pin_valve_for, 1)

# dict for valve independent control
valve_store = {
    1: valve_one,
    2: valve_two,
    3: valve_three,
    4: valve_for
}

def set_duty():
    valve_num = int(input("Enter valve number (1 - 4): ")) 
    duty = float(input('Enetere duty 0 - 100: '))
    valve_store[valve_num].ChangeDutyCycle(duty)
    print(f'duty of valve#{valve_num} = {duty} %')


def set_freq():
    valve_num = int(input("Enter valve number (1 - 4): ")) 
    freq = float(input('Enter freq 1 - 8500 Hz: '))
    valve_store[valve_num].ChangeFrequency(freq)
    print(f'freq of valve#{valve_num} = {freq} Hz')


def sw_exit():
    GPIO.cleanup()
    print("Goodbay!!")
    sys.exit()


def sw_start():
    valve_num = int(input("Enter valve number (1 - 4): ")) 
    valve_store[valve_num].start(50)
    print(f"Strat valve#{valve_num} with duty 50%")


def sw_stop():
    valve_num = int(input("Enter valve number (1 - 4): ")) 
    valve_store[valve_num].stop()
    print(f"Stop valve#{valve_num}")


def selector(cmd):
    switcher = {
        'd': set_duty,
        'f': set_freq,
        'p': sw_start,
        's': sw_stop,
        'q': sw_exit
    }
    out = switcher.get(cmd, lambda: print("Error"))
    return out()


def main():
    while True:
        cmd = input('perss d to set duty, prss f to set freq, press p to start, press s to stop, press q tp exit ')
        selector(cmd)


main()
