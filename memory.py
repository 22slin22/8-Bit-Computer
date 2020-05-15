import ROM
import sys

CLEAR = False


INSTRUCTIONS = {
	"HLT"			:	0x00,
	"NOOP"			:	0xf0,
	"MOV A, #"		:	0x11,
	"MOV A, a"		:	0x12,
	"MOV A, @"		:	0x13,
	"MOV A, (SP)"	:	0x15,
	"MOV A, SPL"	:	0x16,
	"MOV A, SPH"	:	0x17,
	"MOV IOA, A"	:	0x18,
	"MOV IOA, #"	:	0x19,
	"MOV IOA, a"	:	0x1a,
	"MOV IOA, @"	:	0x1b,
	"MOV IOA, (SP)"	:	0x1d,
	"MOV SPL, A"	:	0x28,
	"MOV SPH, A"	:	0x2a,
	"MOV SP, #"		:	0x2c,
	"MOV SP, a"		:	0x2d,
	"MOV (SP), A"	:	0x30,
	"MOV (SP), #"	:	0x31,
	"MOV (SP), a"	:	0x32,
	"MOV (SP), SPL"	:	0x36,
	"MOV (SP), SPH"	:	0x37,
	"MOV a, A"		:	0x38,
	"MOV a, SP"		:	0x3a,
	"MOV @, A"		:	0x3c,
	"ADD A"			:	0x40,
	"ADD #"			:	0x41,
	"ADD a"			:	0x42,
	"ADD @"			:	0x43,
	"ADD (SP)"		:	0x45,
	"ADDC A"		:	0x48,
	"ADDC #"		:	0x49,
	"ADDC a"		:	0x4a,
	"ADDC @"		:	0x4b,
	"ADDC (SP)"		:	0x4d,
	"SUB #"			:	0x51,
	"SUB a"			:	0x52,
	"SUB @"			:	0x53,
	"SUB (SP)"		:	0x55,
	"SUBB #"		:	0x59,
	"SUBB a"		:	0x5a,
	"SUBB @"		:	0x5b,
	"SUBB (SP)"		:	0x5d,
	"INC SP"		:	0x60,
	"DEC SP"		:	0x61,
	"COMP #"		:	0x71,
	"COMP a"		:	0x72,
	"COMP @"		:	0x73,
	"COMP (SP)"		:	0x75,
	"OUT A"			:	0x80,
	"OUT #"			:	0x81,
	"OUT a"			:	0x82,
	"OUT @"			:	0x83,
	"OUT (SP)"		:	0x85,
	"IN A"			:	0x88,
	"IN a"			:	0x8a,
	"IN @"			:	0x8b,
	"JMP #"			:	0x90,
	"JMPZ #"		:	0x92,
	"JMPNZ #"		:	0x93,
	"JMPC #"		:	0x94,
	"JMPNC #"		:	0x95,
	"JMPS #"		:	0x96,
	"JMPNS #"		:	0x97,
	"JMP a"			:	0x98,
	"JMPZ a"		:	0x99,
	"JMPNZ a"		:	0x9a,
	"JMPC a"		:	0x9b,
	"JMPNC a"		:	0x9c,
	"JMPS a"		:	0x9d,
	"JMPNS a"		:	0x9e,
	"PUSH A"		:	0xa0,
	"PUSH #"		:	0xa1,
	"PUSH a"		:	0xa2,
	"PUSH w"		:	0xa6,
	"PUSH PC+3"		:	0xa7,
	"POP A"			:	0xa8,
	"POP PC"		:	0xae,
}


assert len(sys.argv) > 1, "You have to specify a file to write to memory as an argument"

file = open(sys.argv[1], "r")

ROM.init()
if CLEAR:
	ROM.fill(0xff)

address = 0

key_points = {}
placeholders = {}

for line in file:
	line = line.strip()
	# Skip empty line and lines with only whitespaces
	if not line:
		continue

	if line.endswith(":"):
		line = line[:-1]
		key_points[line] = address
		# don't count this as a memory byte
		continue

	elif line.startswith("[") and line.endswith("]"):
		placeholders[address] = line[1:-1]
		# skip an additional line to make room for the 2 byte of the address
		address += 1

	elif line.startswith("@"):
		line = line[1:]
		if line.startswith("0x"):
			line = line[2:]
			val = int(line, 16)
			address = val
			continue
		else:
			raise ValueError("Incorrect address marker: {}".format(line))

	elif line in INSTRUCTIONS:
		ROM.write(address, INSTRUCTIONS[line])
		print(address, hex(INSTRUCTIONS[line]))

	elif line.startswith("0x"):
		line = line[2:]
		val = int(line, 16)
		if len(line) == 2:
			ROM.write(address, val)
			print(address, hex(val))
		elif len(line) == 4:
			ROM.write(address, val >> 8)
			address += 1
			ROM.write(address, val)
			print(address, hex(val))
		else:
			raise ValueError("Hex Value must be of length 2 or 4. Value: 0x{0}".format(line))

	elif line.startswith("0b"):
		val = int(line[2:], 2)
		ROM.write(address, val)
		print(address, bin(val))

	elif line.startswith("'") and line.endswith("'"):
		val = ord(line[1:-1])
		ROM.write(address, val)
		print(address, chr(val))

	else:
		val = int(line)
		ROM.write(address, val)
		print(address, val)

	address += 1


# replace all the placeholders
for address, key_point in placeholders.items():
	val = key_points[key_point]
	ROM.write(address, val >> 8)
	ROM.write(address + 1, val)
	print(address, val)

file.close()
ROM.cleanup()
