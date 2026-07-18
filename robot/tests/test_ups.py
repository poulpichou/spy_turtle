from robot.hardware.ups_hat import UPSHat

ups=UPSHat()

print("Cells      :",ups.batteries())
print("Voltage    :",ups.voltage(),"V")
print("Current    :",ups.current(),"mA")
print("Battery    :",ups.percentage(),"%")
print("Remaining  :",ups.remaining_capacity(),"mAh")
print("Discharge  :",ups.remaining_discharge(),"min")
print("Charge     :",ups.remaining_charge(),"min")
print("USB        :",ups.usb_present())
print("Charging   :",ups.charging())