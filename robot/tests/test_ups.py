from smbus2 import SMBus
import time

bus=SMBus(1)
addr=0x2d

while True:
    values=[bus.read_byte_data(addr,i) for i in range(0x60)]

    print("-"*60)

    for i,v in enumerate(values):
        print(f"{i:02X}: {v:02X}")

    time.sleep(1)