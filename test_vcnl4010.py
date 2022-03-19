from __future__  import print_function
from VCNL4010    import VCNL4010
import RPi.GPIO as GPIO
import time

v4010 = VCNL4010(debug=False)

# this is called when an interrupt is detected
def int_event(pin):
	check_int()
	print(v4010.read_flags())

int_pin = 14 # BCM pin 14
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # BCM pin-numbering scheme
GPIO.setup(int_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(int_pin, GPIO.FALLING, callback=int_event)

def check_int():
	if (GPIO.input(int_pin)):
		print("INT pin is high, no interrupt")
	else:
		print("INT pin is low, interrupt is active")

print("--> Restore default values manually")
v4010.restore_default_values()
time.sleep(1)
print("--> Print all non-default values, all sensor data is invalid as sensors are not enabled")
for bit_field in v4010.check_default_values():
	v4010.read_bf_and_print(bit_field)
print("--> Enable ALS")
v4010.i2c_bf_write(v4010.BF_SELFTIMED_EN, v4010.BF_SELFTIMED_EN.TABLE_ENUM["ENABLE"])
v4010.i2c_bf_write(v4010.BF_ALS_EN, v4010.BF_ALS_EN.TABLE_ENUM["ENABLE"])
time.sleep(1)
check_int()
print("--> Check ALS interrupts")
v4010.i2c_bf_write(v4010.BF_INT_THRES_SEL, v4010.BF_INT_THRES_SEL.TABLE_ENUM["ALS_SEL"])
v4010.i2c_bf_write(v4010.BF_INT_THRES_EN, v4010.BF_INT_THRES_EN.TABLE_ENUM["ENABLE"])
v4010.i2c_bf_write(v4010.BF_HIGH_THRES, 0x0000)
time.sleep(1) # expect BF_INT_TH_HIGH
v4010.i2c_bf_write(v4010.BF_HIGH_THRES, 0xFFFF) # set to a high value so that INT_TH_HIGH doesn't get set anymore
v4010.i2c_bf_write(v4010.BF_LOW_THRES, 0xFFFF) # set to a high value so that we will see the INT_TH_LOW
time.sleep(1)  # expect INT_TH_LOW
v4010.i2c_bf_write(v4010.BF_LOW_THRES, 0x0000) # set to a low value so that ALS_IF_L_INT doesn't get set anymore
time.sleep(1) # expect nothing
check_int()
print("--> Print all non-default values")
for bit_field in v4010.check_default_values():
	v4010.read_bf_and_print(bit_field)
v4010.i2c_bf_write(v4010.BF_INT_THRES_EN, v4010.BF_INT_THRES_EN.TABLE_ENUM["DISABLE"])
print("--> Check proximity sensor")
v4010.i2c_bf_write(v4010.BF_ALS_EN, v4010.BF_ALS_EN.TABLE_ENUM["DISABLE"])
v4010.i2c_bf_write(v4010.BF_IR_LED_CURRENT, 16) # 160mA
v4010.i2c_bf_write(v4010.BF_PROX_EN, v4010.BF_PROX_EN.TABLE_ENUM["ENABLE"])
for n in range(0,100):
	v4010.read_bf_and_print(v4010.BF_PROX_RESULT)
	time.sleep(0.1)
print("--> Check PROX interrupts")
v4010.i2c_bf_write(v4010.BF_INT_THRES_SEL, v4010.BF_INT_THRES_SEL.TABLE_ENUM["PROX_SEL"])
v4010.i2c_bf_write(v4010.BF_INT_THRES_EN, v4010.BF_INT_THRES_EN.TABLE_ENUM["ENABLE"])
v4010.i2c_bf_write(v4010.BF_HIGH_THRES, 0x0000)
time.sleep(1) # expect BF_INT_TH_HIGH
v4010.i2c_bf_write(v4010.BF_HIGH_THRES, 0xFFFF) # set to a high value so that INT_TH_HIGH doesn't get set anymore
v4010.i2c_bf_write(v4010.BF_LOW_THRES, 0xFFFF) # set to a high value so that we will see the INT_TH_LOW
time.sleep(1)  # expect INT_TH_LOW
v4010.i2c_bf_write(v4010.BF_LOW_THRES, 0x0000) # set to a low value so that ALS_IF_L_INT doesn't get set anymore
time.sleep(1) # expect nothing
check_int()
v4010.i2c_bf_write(v4010.BF_PROX_EN, v4010.BF_PROX_EN.TABLE_ENUM["DISABLE"])
print("--> Print all non-default values")
for bit_field in v4010.check_default_values():
	v4010.read_bf_and_print(bit_field)

