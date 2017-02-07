import logging

from DeviceManager import DeviceManager

logging.root.setLevel(logging.INFO)

manager = DeviceManager("iot1")
try:
    manager.block_receive()
except:
    logging.info("Exception", exc_info=1)
finally:
    manager.cleanup()
