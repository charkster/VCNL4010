from __future__ import print_function
import smbus
import time

class VCNL4010:
	
	def __init__(self, slave_id=0x13, debug=False):
		self.slave_id  = slave_id
		self.bus       = smbus.SMBus(1)
		self.debug     = debug

	class bitfield_type:
		def __init__(self, NAME       = "",
		                   ADDRESS    = 0x00,
		                   RST_VAL    = 0x0000,
		                   WIDTH      = 0,
		                   OFFSET     = 0,
		                   ACCESS     = "",
		                   TABLE_ENUM = {},
		                   OTHER      = "" ):

			self.NAME        = NAME
			self.ADDRESS     = ADDRESS
			self.RST_VAL     = RST_VAL
			self.WIDTH       = WIDTH
			self.OFFSET      = OFFSET
			self.ACCESS      = ACCESS
			self.TABLE_ENUM  = TABLE_ENUM
			self.OTHER       = OTHER
			self.BIT_MASK    = int(2 ** self.WIDTH - 1) << self.OFFSET

	######################################
	# COMMAND REGISTER #0, Address 0x80
	######################################

	# Enables state machine and LP oscillator for self timed measurements 
	# no measurement is performed until the corresponding bit is set
	BF_SELFTIMED_EN = bitfield_type (
	NAME       = "SELFTIMED_EN",
	ADDRESS    = 0x80,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 0,
	ACCESS     = "RW",
	TABLE_ENUM = { "DISABLE" : 0, "ENABLE" : 1 } )

	# Proxity feature enable
	BF_PROX_EN = bitfield_type (
	NAME       = "PROX_EN",
	ADDRESS    = 0x80,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 1,
	ACCESS     = "RW",
	TABLE_ENUM = { "DISABLE" : 0, "ENABLE" : 1 } )

	# Enables periodic als measurement
	BF_ALS_EN = bitfield_type (
	NAME       = "ALS_EN",
	ADDRESS    = 0x80,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 2,
	ACCESS     = "RW",
	TABLE_ENUM = { "DISABLE" : 0, "ENABLE" : 1 } )

	# Starts a single on-demand measurement for proximity.
	# Result is available at the end of conversion for reading in the registers #7(HB) and #8(LB).
	BF_PROX_OD = bitfield_type (
	NAME       = "PROX_OD",
	ADDRESS    = 0x80,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 3,
	ACCESS     = "RW",
	TABLE_ENUM = { "TRIGGER" : 1 } )

	# Starts a single on-demand measurement for ambient light.
	# If averaging is enabled, starts a sequence of readings and stores
	# the averaged result. Result is available at the end of conversion 
	# for reading in the registers #5(HB) and #6(LB). 
	BF_ALS_OD = bitfield_type (
	NAME       = "ALS_OD",
	ADDRESS    = 0x80,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 4,
	ACCESS     = "RW",
	TABLE_ENUM = { "TRIGGER" : 1 } )

	# Value = 1 when proximity measurement data is available in the
	# result registers. This bit will be reset when one of the 
	# corresponding result registers (reg #7, reg #8) is read.
	BF_PROX_DATA_RDY = bitfield_type (
	NAME       = "PROX_DATA_RDY",
	ADDRESS    = 0x80,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 5,
	ACCESS     = "RO",
	TABLE_ENUM = { "NOT_READY" : 0, "READY" : 1 } )
	
	# Value = 1 when ambient light measurement data is available in the 
	# result registers. This bit will be reset when one of the 
	# corresponding result registers (reg #5, reg #6) is read.
	BF_ALS_DATA_RDY = bitfield_type (
	NAME       = "ALS_DATA_RDY",
	ADDRESS    = 0x80,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 6,
	ACCESS     = "RO",
	TABLE_ENUM = { "NOT_READY" : 0, "READY" : 1 } )
	
	# ???
	BF_CONFIG_LOCK = bitfield_type (
	NAME       = "CONFIG_LOCK",
	ADDRESS    = 0x80,
	RST_VAL    = 0x01,
	WIDTH      = 1,
	OFFSET     = 7,
	ACCESS     = "RO",
	TABLE_ENUM = { "UNLOCKED" : 0, "LOCKED" : 1 } )
	
	###########################################
	# PROXIMITY RATE REGISTER #2 ADDRESS 0x82
	###########################################
	
	# Rate of Proximity Measurement (no. of measurements per second)
	# 2 ^ (value + 1), 0 is 2 meas/s, 1 is 4 meas/s, etc...
	BF_PROXIMITY_RATE = bitfield_type (
	NAME       = "PROXIMITY_RATE",
	ADDRESS    = 0x82,
	RST_VAL    = 0x00,
	WIDTH      = 3,
	OFFSET     = 0,
	ACCESS     = "RW",
	TABLE_ENUM = { "1.95 meas/s" : 0, "3.9 meas/s" : 1, "7.8 meas/s" : 2, "16.6 meas/s" : 3, "31 meas/s" : 4, "62 meas/s" : 5, "125 meas/s" : 6, "250 meas/s" : 7 } )

	###########################################
	# IR LED CURRENT REGISTER #3 ADDRESS 0x83
	###########################################
	
	# IR LED current = Value (dec.) x 10 mA.
	# LED Current is limited to 200 mA for values higher as 20d. 
	BF_IR_LED_CURRENT = bitfield_type (
	NAME       = "IR_LED_CURRENT",
	ADDRESS    = 0x83,
	RST_VAL    = 0x02,
	WIDTH      = 5,
	OFFSET     = 0,
	ACCESS     = "RW",
	TABLE_ENUM = { } )
	
	####################################################
	# AMBIENT LIGHT PARAMETER REGISTER #4 ADDRESS 0x84
	####################################################
	
	# Bit values sets the number of single conversions done during one 
	# measurement cycle. Result is the average value of all conversions.
	# 2 ^ value, 0 is 1 measurement, 1 is 2 meas... 7 is 128 meas
	BF_AMBIENT_AVERAGING = bitfield_type (
	NAME       = "AMBIENT_AVERAGING",
	ADDRESS    = 0x84,
	RST_VAL    = 0x05,
	WIDTH      = 3,
	OFFSET     = 0,
	ACCESS     = "RW",
	TABLE_ENUM = { "1 conv" : 0, "2 conv" : 1, "4 conv" : 2, "8 conv" : 3, "16 conv" : 4, "32 conv" : 5, "64 conv" : 6, "128 conv" : 7 } )
	
	# With active auto offset compensation the offset value is measured
	# before each ambient light measurement and subtracted automatically
	# from actual reading. 
	BF_ABIENT_AUTO_OFFSET_COMP = bitfield_type (
	NAME       = "AMBIENT_AUTO_OFFSET_COMP",
	ADDRESS    = 0x84,
	RST_VAL    = 0x01,
	WIDTH      = 1,
	OFFSET     = 3,
	ACCESS     = "RW",
	TABLE_ENUM = { "DISABLE" : 0, "ENABLE" : 1 } )
	
	# Ambient light measurement rate
	# value + 1, 0 is 1 sample/s, 1 is 2 samples/s, etc...
	BF_AMBIENT_ALS_RATE = bitfield_type (
	NAME       = "AMBIENT_ALS_RATE",
	ADDRESS    = 0x84,
	RST_VAL    = 0x01,
	WIDTH      = 3,
	OFFSET     = 4,
	ACCESS     = "RW",
	TABLE_ENUM = { "1 samp/s" : 0, "2 samp/s" : 1, "3 samp/s" : 2, "4 samp/s" : 3, "5 samp/s" : 4, "6 samp/s" : 5, "8 samp/s" : 6, "10 samp/s" : 7 } )
	
	# This function can be used for performing faster ambient light measurements.
	BF_ABIENT_CONT_CONV_MODE = bitfield_type (
	NAME       = "AMBIENT_CONT_CONV_MODE",
	ADDRESS    = 0x84,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 7,
	ACCESS     = "RW",
	TABLE_ENUM = { "DISABLE" : 0, "ENABLE" : 1 } )
	
	#################################################
	# AMBIENT LIGHT RESULT REGISTER #5 ADDRESS 0x85, 0x86
	#################################################
	
	BF_AMBIENT_RESULT = bitfield_type (
	NAME       = "AMBIENT_RESULT",
	ADDRESS    = 0x85,
	RST_VAL    = 0x0000,
	WIDTH      = 16,
	OFFSET     = 0,
	ACCESS     = "RO",
	TABLE_ENUM = { } )
	
	#############################################
	# PROXIMITY RESULT REGISTER #7 ADDRESS 0x87
	#############################################
	
	BF_PROX_RESULT = bitfield_type (
	NAME       = "PROX_RESULT",
	ADDRESS    = 0x87,
	RST_VAL    = 0x0000,
	WIDTH      = 16,
	OFFSET     = 0,
	ACCESS     = "RO",
	TABLE_ENUM = { } )
	
	##############################################
	# INTERRUPT CONTROL REGISTER #9 ADDRESS 0x89
	##############################################
	
	# If 0: thresholds are applied to proximity measurements
	# If 1: thresholds are applied to als measurements
	BF_INT_THRES_SEL = bitfield_type (
	NAME       = "INT_THRES_SEL",
	ADDRESS    = 0x89,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 0,
	ACCESS     = "RW",
	TABLE_ENUM = { "PROX_SEL" : 0, "ALS_SEL" : 1} )
	
	# Enables interrupt generation when high or low threshold is exceeded
	BF_INT_THRES_EN = bitfield_type (
	NAME       = "INT_THRES_EN",
	ADDRESS    = 0x89,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 1,
	ACCESS     = "RW",
	TABLE_ENUM = { "DISABLE" : 0, "ENABLE" : 1 } )
	
	#  Enables interrupt generation at ambient data ready
	BF_INT_ALS_DATA_RDY_EN = bitfield_type (
	NAME       = "INT_ALS_DATA_RDY_EN",
	ADDRESS    = 0x89,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 2,
	ACCESS     = "RW",
	TABLE_ENUM = { "DISABLE" : 0, "ENABLE" : 1 } )
	
	#  Enables interrupt generation at proximity data ready
	BF_INT_PROX_DATA_RDY_EN = bitfield_type (
	NAME       = "INT_PROX_DATA_RDY_EN",
	ADDRESS    = 0x89,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 3,
	ACCESS     = "RW",
	TABLE_ENUM = { "DISABLE" : 0, "ENABLE" : 1 } )

	# These bits contain the number of consecutive measurements needed
	# above/below the threshold
	# 2 ^ value, 0 is 1 count, 1 is 2 counts... 7 is 128 counts 
	BF_INT_COUNT_EXCEED = bitfield_type (
	NAME       = "INT_COUNT_EXCEED",
	ADDRESS    = 0x89,
	RST_VAL    = 0x00,
	WIDTH      = 3,
	OFFSET     = 5,
	ACCESS     = "RW",
	TABLE_ENUM = { "1 cnt" : 0, "2 cnt" : 1, "4 cnt" : 2, "8 cnt" : 3, "16 cnt" : 4, "32 cnt" : 5, "64 cnt" : 6, "128 cnt" : 7 } )
	
	################################################
	# LOW THRESHOLD UPPER REGISTER #10 ADDRESS 0x8A
	################################################
	
	BF_LOW_THRES = bitfield_type (
	NAME       = "LOW_THRES",
	ADDRESS    = 0x8A,
	RST_VAL    = 0x0000,
	WIDTH      = 16,
	OFFSET     = 0,
	ACCESS     = "RW",
	TABLE_ENUM = { } )
	
	#################################################
	# HIGH THRESHOLD UPPER REGISTER #12 ADDRESS 0x8C
	#################################################
	
	BF_HIGH_THRES = bitfield_type (
	NAME       = "HIGH_THRES",
	ADDRESS    = 0x8C,
	RST_VAL    = 0xFFFF,
	WIDTH      = 16,
	OFFSET     = 0,
	ACCESS     = "RW",
	TABLE_ENUM = { } )
	
	#############################################
	# INTERRUPT STATUS REGISTER #14 ADDRESS 0x8E
	#############################################
	
	# Indicates a high threshold exceed
	# Write 1 to clear
	BF_INT_TH_HI = bitfield_type (
	NAME       = "INT_TH_HI",
	ADDRESS    = 0x8E,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 0,
	ACCESS     = "RW",
	TABLE_ENUM = { "NOT_EXCEEDED" : 0, "EXCEEDED" : 1},
	OTHER      = "INT_STATUS" )
	
	# Indicates a low threshold exceed
	# Write 1 to clear
	BF_INT_TH_LOW = bitfield_type (
	NAME       = "INT_TH_LOW",
	ADDRESS    = 0x8E,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 1,
	ACCESS     = "RW",
	TABLE_ENUM = { "NOT_EXCEEDED" : 0, "EXCEEDED" : 1 },
	OTHER      = "INT_STATUS" )
	
	# Enables interrupt generation at ambient data ready
	# Write 1 to clear
	BF_INT_ALS_DATA_RDY = bitfield_type (
	NAME       = "INT_ALS_DATA_RDY",
	ADDRESS    = 0x8E,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 2,
	ACCESS     = "RW",
	TABLE_ENUM = { "NOT_SET" : 0, "SET" : 1 },
	OTHER      = "INT_STATUS" )
	
	# Enables interrupt generation at proximity data ready
	# Write 1 to clear
	BF_INT_PROX_DATA_RDY = bitfield_type (
	NAME       = "INT_PROX_DATA_RDY",
	ADDRESS    = 0x8E,
	RST_VAL    = 0x00,
	WIDTH      = 1,
	OFFSET     = 3,
	ACCESS     = "RW",
	TABLE_ENUM = { "NOT_SET" : 0, "SET" : 1 },
	OTHER      = "INT_STATUS" )

	#########################################################
	# PROXIMITY MODULATOR TIMING ADJUSTMENT #15 ADDRESS 0x8F
	#########################################################
	
	# Setting a dead time in evaluation of IR signal at the slopes of
	# the IR signal. ???
	BF_MODULATION_DEAD_TIME = bitfield_type (
	NAME       = "MODULATION_DEAD_TIME",
	ADDRESS    = 0x8F,
	RST_VAL    = 0x01,
	WIDTH      = 3,
	OFFSET     = 0,
	ACCESS     = "RW",
	TABLE_ENUM = { } )

	# The proximity measurement is using a square IR signal as measurement signal
	BF_PROXIMITY_FREQUENCY= bitfield_type (
	NAME       = "PROXIMITY_FREQUENCY",
	ADDRESS    = 0x8F,
	RST_VAL    = 0x00,
	WIDTH      = 2,
	OFFSET     = 3,
	ACCESS     = "RW",
	TABLE_ENUM = { "390.625 kHz": 0, "781.25 kHz": 1, "1.5625 MHz": 2, "3.125 MHz": 3} )

	# Setting a delay time between IR LED signal and IR input signal evaluation
	# ???
	BF_MODULATION_DELAY_TIME = bitfield_type (
	NAME       = "MODULATION_DELAY_TIME",
	ADDRESS    = 0x8F,
	RST_VAL    = 0x00,
	WIDTH      = 3,
	OFFSET     = 5,
	ACCESS     = "RW",
	TABLE_ENUM = { } )

	LIST_OF_BIT_FIELDS = [ BF_SELFTIMED_EN, BF_PROX_EN, BF_ALS_EN, BF_PROX_OD, BF_ALS_OD, BF_PROX_DATA_RDY, BF_ALS_DATA_RDY, BF_CONFIG_LOCK, BF_PROXIMITY_RATE, BF_IR_LED_CURRENT, BF_AMBIENT_AVERAGING, BF_ABIENT_AUTO_OFFSET_COMP, BF_AMBIENT_ALS_RATE, BF_ABIENT_CONT_CONV_MODE, BF_AMBIENT_RESULT, BF_PROX_RESULT, BF_INT_THRES_SEL, BF_INT_THRES_EN, BF_INT_ALS_DATA_RDY_EN, BF_INT_PROX_DATA_RDY_EN, BF_INT_COUNT_EXCEED, BF_LOW_THRES, BF_HIGH_THRES, BF_INT_TH_HI, BF_INT_TH_LOW, BF_INT_ALS_DATA_RDY, BF_INT_PROX_DATA_RDY, BF_MODULATION_DEAD_TIME, BF_PROXIMITY_FREQUENCY, BF_MODULATION_DELAY_TIME ]
	
	LIST_OF_INT_BIT_FIELDS = [ BF_INT_TH_HI, BF_INT_TH_LOW, BF_INT_ALS_DATA_RDY, BF_INT_PROX_DATA_RDY ]
	
	# swap_bytes is needed as VCNL4010 is big endian and smbus word function are little endian
	def swap_bytes(self, data):
		return ((data & 0xFFFF) >> 8) + ((data & 0x00FF) << 8)
	
	def i2c_bf_read(self, bit_field):
		try:
			address  = 0xFF & bit_field.ADDRESS
			if (bit_field.WIDTH > 8):
				bf_read_data = ( self.swap_bytes(self.bus.read_word_data(self.slave_id, address)) & bit_field.BIT_MASK ) >> bit_field.OFFSET
			else:
				bf_read_data = ( self.bus.read_byte_data(self.slave_id, address) & bit_field.BIT_MASK ) >> bit_field.OFFSET
			if (self.debug):
				print("Read bit_field {} address 0x{:02x}, bit mask is 0x{:04x}, value is 0x{:02x}".format(bit_field.NAME, address, bit_field.BIT_MASK, bf_read_data))
			return bf_read_data
		except:
			print("ERROR with i2c_bf_read")
	
	def i2c_bf_write(self, bit_field, bf_wdata):
		try:
			address = 0xFF & bit_field.ADDRESS
			if (bit_field.WIDTH > 8):
				read_data = self.bus.read_word_data(self.slave_id, address)
			else:
				read_data = self.bus.read_byte_data(self.slave_id, address)
			wdata = (read_data & ~bit_field.BIT_MASK) | ((bf_wdata << bit_field.OFFSET) & bit_field.BIT_MASK)
			if (bit_field.WIDTH > 8):
				self.bus.write_word_data(self.slave_id, address, self.swap_bytes(wdata))
			else:
				self.bus.write_byte_data(self.slave_id, address, wdata)
			if (self.debug):
				print("Wrote bit_field {} address 0x{:02x}, bit mask is 0x{:04x}, data 0x{:02x}".format(bit_field.NAME, address, bit_field.BIT_MASK, bf_wdata))
		except:
			print("ERROR with i2c_bf_write")

	def read_flags(self):
		list_of_flags = []
		for bit_field in self.LIST_OF_INT_BIT_FIELDS:
			if (self.i2c_bf_read(bit_field) == 1):
				list_of_flags.append(bit_field.NAME)
				self.i2c_bf_write(bit_field, 0x01) # clear
		return list_of_flags

	def check_default_values(self):
		list_of_bit_fields = []
		for bit_field in self.LIST_OF_BIT_FIELDS:
			if (self.i2c_bf_read(bit_field) != bit_field.RST_VAL):
				list_of_bit_fields.append(bit_field)
				if (self.debug):
					print(bit_field.NAME)
		return list_of_bit_fields

	def restore_default_values(self):
		for bit_field in self.LIST_OF_BIT_FIELDS:
			if (bit_field.ACCESS == "RW"):
				self.i2c_bf_write(bit_field, bit_field.RST_VAL)

	def get_key(self, val, my_dict):
		for key, value in my_dict.items():
			if val == value:
				return key

	def read_bf_and_print(self, bit_field):
		value = self.i2c_bf_read(bit_field)
		if (len(bit_field.TABLE_ENUM) != 0):
			print("Bit Field {} is {}".format(bit_field.NAME, self.get_key(value,bit_field.TABLE_ENUM)))
		else:
			print("Bit Field {} has value 0x{:04x}".format(bit_field.NAME, value))
	
