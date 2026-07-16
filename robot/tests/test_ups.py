from smbus2 import SMBus
import time

ADDRESS = 0x2d

bus = SMBus(1)

print("Reading UPS HAT...")

for reg in range(0x00, 0x10):
    try:
        value = bus.read_byte_data(ADDRESS, reg)
        print(f"Register {hex(reg)} : {hex(value)}")
    except Exception as e:
        print(f"Register {hex(reg)} error: {e}")

bus.close()
