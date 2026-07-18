from robot.hardware.ups_hat import UPSHat

ups=UPSHat()

print("Cells:",ups.batteries())
print("Pack :",ups.voltage(),"V")
print("USB  :",ups.usb_present())
print("Charge:",ups.charging())