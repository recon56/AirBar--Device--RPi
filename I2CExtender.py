import time
import threading
from ABE_helpers import ABEHelpers
from ABE_IoPi import IoPi
import numpy as np
import RPi.GPIO as GPIO

__author__ = 'recon'


class IOPlus(threading.Thread):
    def __init__(self, thread_id, c_variable, name, i2c_addr, intr_pin):
        # Thread information
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.cv = c_variable

        # I2C information
        self.i2c_helper = ABEHelpers()
        self.i2c_bus = self.i2c_helper.get_smbus()
        self.bus = IoPi(self.i2c_bus, i2c_addr)

        # Pi pin information
        self.intr_pin = intr_pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.intr_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # State of current sensors
        # TODO- Load from file/server in case of power outage: For now pretend that the current state is "correct"
        self.pin_state = self.read_pins()

    def run(self):
        self.monitor_interrupt_pin()

    def read_pins(self):
        return self.bus.read_port(1) << 8 | self.bus.read_port(0)

    def monitor_interrupt_pin(self):
        self.bus.set_interrupt_on_port(0, 0xFF)
        self.bus.set_interrupt_on_port(1, 0xFF)
        while True:
            GPIO.wait_for_edge(self.intr_pin, GPIO.RISING)
            if GPIO.input(self.intr_pin) == 1:
                self.bus.read_interrupt_capture()
                pins = self.read_pins()
                diff = self.pin_state ^ pins
                if diff != 0:
                    self.cv.acquire()
                    self.pin_state = pins
                    # Report Pin Change
                    self.cv.notifyAll()
                    self.cv.release()

    # Old Test function
    # def filler(self, count):
    #     self.cv.acquire()
    #     time.sleep(1)
    #     print("Iteration  ." + self.name + ", %i", count)
    #     self.cv.notifyAll()
    #     self.cv.release()