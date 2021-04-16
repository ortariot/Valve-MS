#!/usr/bin/env python

import RPi.GPIO as GPIO
import asyncio
from pymodbus.version import version
from pymodbus.server.async_io import StartTcpServer
from pymodbus.server.async_io import StartTlsServer
from pymodbus.server.async_io import StartUdpServer
from pymodbus.server.async_io import StartSerialServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from pymodbus.transaction import ModbusRtuFramer, ModbusBinaryFramer
# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)


class valve_gpio():

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        # pin inicialization
        self.pin_valve_one = 2
        self.pin_valve_two = 3
        self.pin_valve_three = 4
        self.pin_valve_for = 5
        # GPIO pin inicialization as OUT
        GPIO.setup(self.pin_valve_one, GPIO.OUT)
        GPIO.setup(self.pin_valve_two, GPIO.OUT)
        GPIO.setup(self.pin_valve_three, GPIO.OUT)
        GPIO.setup(self.pin_valve_for, GPIO.OUT)
        # OUT inicialization as PWM object
        self.valve_one = GPIO.PWM(self.pin_valve_one, 1)
        self.valve_two = GPIO.PWM(self.pin_valve_two, 1)
        self.valve_three = GPIO.PWM(self.pin_valve_three, 1)
        self.valve_for = GPIO.PWM(self.pin_valve_for, 1)
        self.valve_store = {1: self.valve_one, 2: self.valve_two, 3: self.valve_three, 4: self.valve_for}

    def start_pwm(self, valve_num):
        self.valve_store[valve_num].start(50)

    def stop_pwm(self, valve_num):
        self.valve_store[valve_num].stop()

    def set_freq(self, valve_num, freq):
        self.valve_store[valve_num].ChangeFrequency(freq)

    def set_duty(self, valve_num, duty):
        self.valve_store[valve_num].ChangeDutyCycle(duty)
    
    # def set_up(self, valve_num):
    #     GPIO.output(valve_num, GPIO.HIGH)

    # def set_down(self, valve_num):
    #     GPIO.output(valve_num, GPIO.LOW)

    def valve_cleanup():
        GPIO.cleanup()


store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [17]*100),
    co=ModbusSequentialDataBlock(0, [17]*100),
    hr=ModbusSequentialDataBlock(0, [50]*100),
    ir=ModbusSequentialDataBlock(0, [17]*100))

async def run_server():
    context = ModbusServerContext(slaves=store, single=True)
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Ortariot'
    identity.ProductCode = 'VMS'
    identity.VendorUrl = 'https://github.com/ortariot/'
    identity.ProductName = 'Valve Monster Comander'
    identity.ModelName = 'Valve Monster Server'
    identity.MajorMinorRevision = version.short()

    server = await StartTcpServer(context, identity=identity, address=("0.0.0.0", 5020),
                                  allow_reuse_address=True, defer_start=True)

    asyncio.get_event_loop().call_later(20, lambda: server.serve_forever)
    await server.serve_forever()

async def coil_switch(valves):
    valve1_status = False
    valve2_status = False
    valve3_status = False
    valve4_status = False
    while 1:
        valve1 = store.getValues(0x01, 0, 1)
        valve2 = store.getValues(0x01, 1, 1)
        valve3 = store.getValues(0x01, 2, 1)
        valve4 = store.getValues(0x01, 3, 1)
        if valve1 == [1] and valve1_status is False:
            valves.start_pwm(1)
            valve1_status = True
            # print("valve1_on")
        elif valve1 == [0] and valve1_status is True:
            valves.stop_pwm(1)
            valve1_status = False
            # print("valve1_off")
        if valve2 == [1] and valve2_status is False:
            valves.start_pwm(2)
            valve2_status = True
            # print("valve2_on")
        elif valve2 == [0] and valve2_status is True:
            valves.stop_pwm(2)
            valve2_status = False
            # print("valve2_off")
        if valve3 == [1] and valve3_status is False:
            valves.start_pwm(3)
            valve3_status = True
            # print("valve3_on")
        elif valve3 == [0] and valve3_status is True:
            valves.stop_pwm(3)
            valve3_status = False
            # print("valve3_off")
        if valve4 == [1] and valve4_status is False:
            valves.start_pwm(4)
            valve4_status = True
            # print("valve4_on")
        elif valve4 == [0] and valve4_status is True:
            valves.stop_pwm(4)
            valve4_status = False
            # print("valve4_off")
        await asyncio.sleep(5)

async def duty_change(valves):
    vlv1_duty = store.getValues(0x03, 0, 1)
    vlv2_duty = store.getValues(0x03, 1, 1)
    vlv3_duty = store.getValues(0x03, 2, 1)
    vlv4_duty = store.getValues(0x03, 3, 1)    
    while True:
        if vlv1_duty != store.getValues(0x03, 0, 1):
            vlv1_duty = store.getValues(0x03, 0, 1)
            valves.set_duty(1, vlv1_duty[0])
        if vlv2_duty != store.getValues(0x03, 1, 1):
            vlv2_duty = store.getValues(0x03, 1, 1)
            valves.set_duty(2, vlv2_duty[0])
        if vlv3_duty != store.getValues(0x03, 2, 1):
            vlv3_duty = store.getValues(0x03, 2, 1)
            valves.set_duty(3, vlv3_duty[0])
        if vlv4_duty != store.getValues(0x03, 3, 1):
            vlv4_duty = store.getValues(0x03, 3, 1)
            valves.set_duty(4, vlv4_duty)

        # print(vlv1_duty)
        # print(vlv2_duty)
        # print(vlv3_duty)
        # print(vlv4_duty)
        await asyncio.sleep(3)

if __name__ == "__main__":
    valves = valve_gpio()
    valves.set_freq(1, 0.3)
    valves.set_freq(2, 0.3)
    valves.set_freq(3, 0.3)
    valves.set_freq(4, 0.3)

    ioloop = asyncio.get_event_loop()
    tasks = [ioloop.create_task(coil_switch(valves)),
             ioloop.create_task(duty_change(valves)),              
             ioloop.create_task(run_server())]
    wait_tasks = asyncio.wait(tasks)
    ioloop.run_until_complete(wait_tasks)
    ioloop.close()
    valves.cleanup()

