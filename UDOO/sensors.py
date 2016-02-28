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
        self.values = deque([0, 0, 0])
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

        if self.lastValue > 16500:
            self.lastValue = 16500
        if self.lastValue < 3500:
            self.lastValue = 3500

        self.lastValue = (self.lastValue - 3500) / 130
        self.lastValue = min(self.lastValue, 100)
        self.lastValue = max(self.lastValue, 0)

        self.values.append(self.lastValue)
        self.values.popleft()

        if self.lastValue < 30:
            self.lastValue = (self.lastValue * 100) / 80
        else:
            self.lastValue = 50 + ((self.lastValue-70) * 100) / 70


    def read(self):

        mean = np.mean(self.values)
        std = np.std(self.values)
        data = [x for x in self.values if abs(x - mean) <= 3 * std]

        if not data:
            return self.lastValue
        return np.mean(data)


class SRF03(Sensor):

    def __init__(self, other_sensor):
        self.other_sensor = other_sensor

    def measure(self):
        pass

    def read(self):
        return max((85 - self.other_sensor.read()), 0)


class Z1(Sensor):

    def __init__(self, device, rate):
        try:
            import serial
            self.ser = serial.Serial(device, rate, timeout=5)
            self.lastValue = 0

        except Exception as e:
            print(e)

    def measure(self):
        self.ser.write(bytearray([0x01]))
        time.sleep(5)
        self.lastValue = self.ser.read(2)

    def read(self):
        return self.lastValue


class RandomSensor(Sensor):

    def read(self):
        return np.random.randint(4000, 5000)


class Sensors:
    def __init__(self):
        srf02 = SRF02(3, 0x70)
        self.sensors = [
            srf02,
            SRF03(srf02),
            SRF02(3, 0x72),
        ]

        thr = threading.Thread(target=self.pollSensors, args=(), kwargs={})

        thr.start()

    def addSensor(self, new_sensor):
        self.sensors.append(new_sensor)

    def read(self):
        return [s.read() for s in self.sensors]

    def pollSensors(self):
        while True:
            print "\t\t\t\t\t\t\t\t",
            for s in self.sensors:
                s.measure()
                print s.read(),
            print
