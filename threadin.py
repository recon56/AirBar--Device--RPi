import threading
import I2CExtender

__author__ = 'recon'

if __name__ == "__main__":
    cv = threading.Condition(None)
    cv.acquire()

    i2c = I2CExtender.IOPlus(thread_id="i2c", c_variable=cv, name="I2C",
                             intr_pin=17)
    i2c.start()

    k = 0
    while i2c.is_alive():
        cv.wait()
        cv.acquire()
        print("Sensor Trigger: 0x%04X" % i2c.pin_state)
        cv.release()