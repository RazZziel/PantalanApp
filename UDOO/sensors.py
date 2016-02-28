#!/usr/bin/env python
# coding=utf-8

import threading
import time
import numpy as np


class Sensor(object):
    def read():
        pass


class SRF02(Sensor):

    def __init__(self, bus, address):
        from collections import deque
        self.values = deque([0, 0, 0, 0, 0])
        self.lastValue = 0

        try:
            import smbus

            self.address = address
            self.bus = smbus.SMBus(bus)

        except Exception as e:
            print(e)

    def measure(self):
        self.bus.write_byte_data(self.address, 0, 0x51)
        time.sleep(0.2)
        self.lastValue = self.bus.read_word_data(self.address, 0x02)

        print self.lastValue,

        if self.lastValue > 15000:
            self.lastValue = 0

        self.values.append(self.lastValue)
        self.values.popleft()

    def readLoop(self):
        while True:
            try:
                self.measure()
                self.values.append(self.lastValue)
                self.values.popleft()
            except Exception as e:
                print(e)

    def read(self):

        mean = np.mean(self.values)
        std = np.std(self.values)
        data = [x for x in self.values if abs(x - mean) <= 3 * std]

        if not data:
            return self.lastValue
        return np.mean(data)


class Z1(Sensor):

    def __init__(self, device, rate):
        try:
            import serial
            print "Initializing serial"
            self.ser = serial.Serial(device, rate, timeout=1)
            print "Done"
            self.lastValue = 0

        except Exception as e:
            print(e)

    def measure(self):
        self.ser.write(bytearray([0x01]))
        time.sleep(0.1)
        self.ser.write(bytearray([0x00]))
        self.lastValue = self.ser.read(2)

    def read(self):
        return 123.4


class RandomSensor(Sensor):

    def read(self):
        return np.random.randint(4000, 5000)


class Sensors:
    def __init__(self):
        self.sensors = [
            SRF02(3, 0x70),
            SRF02(3, 0x72),
            Z1('/dev/ttyMCC', 9600)
        ]

        thr = threading.Thread(target=self.pollSensors, args=(), kwargs={})

        thr.start()

    def addSensor(self, new_sensor):
        self.sensors.append(new_sensor)

    def read(self):
        return [s.read() for s in self.sensors]

    def pollSensors(self):
        while True:
            for s in self.sensors:
                s.measure()
                print s.read(),
                time.sleep(0.1)
            print
