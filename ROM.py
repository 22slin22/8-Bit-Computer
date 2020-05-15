#from RPi import GPIO
import time
import re

#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)

# 16 is the LSB and 7 the MSB
IOs = [16, 15, 13, 11, 12, 10, 8, 7]
# 38 is the LSB and 18 is the MSB
ADDRESS_PINS = [38,37,36,35,33,32,31,29,26,24,23,22,21,19,18]
# Write signal for the EEPROM (active low)
WRITE = 40

def init():
	_setup([WRITE])
	_out(WRITE, True)
	_setup(IOs)
	_setup(ADDRESS_PINS)

def cleanup():
	#GPIO.cleanup()
	pass

def _setup(pins):
	for pin in pins:
		#GPIO.setup(pin, GPIO.OUT)
		pass

def _out(pin, bool):
	#GPIO.output(pin, bool)
	pass

def set_address(word):
	for i in range(15):
		if (word & (1 << i)) > 0:
			_out(ADDRESS_PINS[i], True)
		else:
			_out(ADDRESS_PINS[i], False)

def set_byte(byte):
	for i in range(8):
		if (byte & (1 << i)) > 0:
			_out(IOs[i], True)
		else:
			_out(IOs[i], False)

pattern = r'0b10101[01]{7}'
prog = re.compile(pattern)

def write(address, byte):
	if prog.fullmatch(bin(address)):
		print(bin(address), bin(byte))
	set_byte(byte)
	set_address(address)
	_latch()

def _latch():
	# IMPORTANT: leave the sleeps in even if the data sheet sugest you can get faster
	# somehow the writes don't work with shorter sleeps
	time.sleep(0.01)
	_out(WRITE, False)
	time.sleep(0.01)
	_out(WRITE, True)
	time.sleep(0.01)

def fill(byte):
	set_byte(byte)
	for addr in range(1<<15):
		set_address(addr)
		_latch()
