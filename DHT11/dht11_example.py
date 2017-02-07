import RPi.GPIO as GPIO
import dht11
import time
import datetime

# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()

power_io = 6
GPIO.setup(power_io, GPIO.OUT)
GPIO.output(power_io, True)


# read data using pin 22
instance = dht11.DHT11(pin=22)

try:
    while True:
        result = instance.read()
        if result.is_valid():
            print("Last valid input: " + str(datetime.datetime.now()))
            print("Temperature: %d C" % result.temperature)
            print("Humidity: %d %%" % result.humidity)

        time.sleep(1)
except KeyboardInterrupt:
    pass

GPIO.output(power_io, False)
print ("done")
    
