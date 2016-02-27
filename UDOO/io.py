#!/usr/bin/env python
# coding=utf-8

import threading
import time


class Sensor(object):
    def __init__(self, bus, address):
        try:
            import smbus

            self.address = address
            self.bus = smbus.SMBus(bus)

        except Exception as e:
            print(e)

    def read():
        pass


class SRF02(Sensor):

    def __init__(self, bus, address):
        super(SRF02, self).__init__(bus, address)

        from collections import deque
        self.values = deque([0, 0, 0])

        thr = threading.Thread(target=self.readLoop, args=(), kwargs={})

        thr.start()

    def readLoop(self):
        while True:
            self.bus.write_byte_data(self.address, 0, 0x81)
            time.sleep(0.1)
            value = self.bus.read_word_data(self.address, 0x02)

            self.values.popleft()
            self.values.append(value)

    def read(self):

        return sum(self.values) / len(self.values)


class IO:
    def __init__(self):
            self.sensors = [
                SRF02(3, 0x70)
            ]

    def addSensor(self, new_sensor):
        self.sensors.append(new_sensor)

    def read(self):
        return [s.read() for s in self.sensors]
