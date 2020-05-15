'''
the address that the ROMs get is structured as follows:
	I: Intruction 	(MSBF)
	F: FLAGS		(ZERO, CARRY, SIGN)
	S: micro step	(MSBF)

	IIIIIIIIFFFSSSS
'''
import ROM
import re


# ROM_NUM is either 0 or 1 depending which of the the 2 decoder ROM you want to program
# 1: the IN and OUT line decoder
# 0: the other control line decoder
ROM_NUM = 0
CLEAR = False
WRITE_FETCH_CYCLES = False


COMMENT = "#"
STEP_SEPERATOR = "|"
CONTROL_SIGNAL_SEPERATOR = ","

CTRL_LINES = {
	"HL_INC": 1 << 0,
	"PC_INC": 1 << 1,
	#"": 1 << 2,
	"INV": 1 << 3,
	"CARRY_IN": 1 << 4,
	"ALU_OUT": 1 << 5,
	"HLT": 1 << 6,
	"NXT": 1 << 7
}

IN_OUT_LINES = {
	"A_OUT": 	0xf0,
	"B_OUT": 	0xf1,
	"M_OUT": 	0xf2,
	"TMP_OUT": 	0xf3,
	"PCH_OUT": 	0xf4,
	"PCL_OUT": 	0xf5,
	"SPH_OUT": 	0xf6,
	"SPL_OUT": 	0xf7,
	"IN": 		0xf8,

	"IR_IN":	0x0f,
	"A_IN":		0x1f,
	"SP_INC":	0x2f,
	"TMP_IN":	0x3f,
	"SPH_IN":	0x4f,
	"SPL_IN":	0x5f,
	"SP_DEC":	0x6f,
	"OUT":		0x7f,
	"H_IN":		0x8f,
	"L_IN":		0x9f,
	"PCH_IN":	0xaf,
	"PCL_IN":	0xbf,
	"IOA_IN":	0xcf,
	"M_IN":		0xdf
}

FLAGS = {
	"010": re.compile('1[01][01]'),	# Zero
	"011": re.compile('0[01][01]'),	# not Zero
	"100": re.compile('[01]1[01]'),	# Carry
	"101": re.compile('[01]0[01]'),	# not Carry
	"110": re.compile('[01][01]1'),	# Sign
	"111": re.compile('[01][01]0'),	# not Sign
}


FETCH = [
	["PCH_OUT", "H_IN"],
	["PCL_OUT", "L_IN"],
	["M_OUT","IR_IN", "PC_INC"]
]

SKIP_JMP = [
	["HL_INC", "PC_INC"],
	["HL_INC", "PC_INC"],
	["NXT"]
]


def print_latex(instruction_line, micro_step_line):
	print(instruction_line)
	micro_step_line = micro_step_line.replace("|", " \\\\ ")
	micro_step_line = micro_step_line.replace("_", "\\_")
	print(micro_step_line)


def clean_line(line, file):
	# Check if the end of the file has been reaches (empty line are represented as '\n')
	if line == '':
		return None

	# delete the comment
	comment_char_index = line.find(COMMENT)
	if comment_char_index != -1:
		line = line[:comment_char_index]

	# remove leading and trailing spaces
	line = line.strip()
	# skip empty lines (and lines with only whitespaces)
	if not line:
		# Get the next line
		return clean_line(file.readline(), file)
	return line


def write_fetch_cycles():
	# Go through all possible instructinos and flags
	for i in range(1<<11):
		for step, conrtol_lines in enumerate(FETCH):
			address = i << 4 | step

			if ROM_NUM == 0:
				byte = 0
				for signal in conrtol_lines:
					if signal in CTRL_LINES:
						byte = byte | CTRL_LINES[signal]

				# Invert active low signals (ALU_OUT, HLT, NXT)
				byte = byte ^ 0b11100000
			
			else:
				# no In and OUT line is 0xff
				byte = 0xff
				for signal in conrtol_lines:
					if signal in IN_OUT_LINES:
						byte = byte & IN_OUT_LINES[signal]					

			ROM.write(address, byte)

ROM.init()

if CLEAR:
	# Clear the ROM (Fill it with HLTs)
	if ROM_NUM == 0:

		byte = CTRL_LINES["HLT"]
		# Invert active low signals (ALU_OUT, HLT, NXT)
		byte = byte ^ 0b11100000
		ROM.fill(byte)

	else:
		# All 1s is no IN and not OUT
		ROM.fill(0xff)
if WRITE_FETCH_CYCLES:
	write_fetch_cycles()

file = open("intsructions-micro-steps.txt", "r")

instruction_line = clean_line(file.readline(), file)
micro_step_line = clean_line(file.readline(), file)

# If both lines are not empty
while instruction_line and micro_step_line:
	# print_latex(instruction_line, micro_step_line)

	assert len(instruction_line) == 8, "An intruction has to be 8 bits long. instruction is {0}".format(instruction_line)

	# Seperate the steps of the instruction
	steps = micro_step_line.split(STEP_SEPERATOR)
	# Seperate the control signals
	steps = [s.split(CONTROL_SIGNAL_SEPERATOR) for s in steps]

	# Check if instruction is flag depandent
	if not "FFF" in instruction_line:
		# Get decimal value of the instruction
		instruction = int(instruction_line, 2)

		# Go through all flags (3) because the instruction is not dependent on them
		for flag in range(1<<3):
			for step, conrtol_lines in enumerate(steps):
				# Step + 3 because the first 3 steps are the fetch cycle
				address = instruction << 7 | flag << 4 | (step + 3)

				# Get the byte to write to the EEPROM
				if ROM_NUM == 0:
					byte = 0
					for signal in conrtol_lines:
						if signal in CTRL_LINES:
							byte = byte | CTRL_LINES[signal]

					# Invert active low signals (ALU_OUT, HLT, NXT)
					byte = byte ^ 0b11100000

					#test = byte & (1 << 5)
					#if not test:
					#	print('{0:015b}   {1:08b}   {2:08b}'.format(address, instruction, byte))
					'''
					if instruction == 0b00010101:
						print('{0:015b}   {1:08b}'.format(address, byte))
						print(instruction_line)
						print(micro_step_line)
					'''

				else:
					# no In and OUT line is 0xff
					byte = 0xff
					for signal in conrtol_lines:
						if signal in IN_OUT_LINES:
							byte = byte & IN_OUT_LINES[signal]

				ROM.write(address, byte)

	else:
		# Instruction is flag dependent
		for flag, regex in FLAGS.items():
			instruction = instruction_line.replace("FFF", flag)
			instruction = int(instruction, 2)

			for flag_permutation in range(1<<3):
				# Convert the int into a 3 bit long binary value
				flag_str = '{0:03b}'.format(flag_permutation)
				# Check if the specific flag is set / not set
				if re.match(regex, flag_str) is not None:
					for step, conrtol_lines in enumerate(steps):
						# Step + 3 because the first 3 steps are the fetch cycle
						address = instruction << 7 | flag_permutation << 4 | (step + 3)

						# Get the byte to write to the EEPROM
						if ROM_NUM == 0:
							byte = 0
							for signal in conrtol_lines:
								if signal in CTRL_LINES:
									byte = byte | CTRL_LINES[signal]

							# Invert active low signals (ALU_OUT, HLT, NXT)
							byte = byte ^ 0b11100000

						else:
							# no In and OUT line is 0xff
							byte = 0xff
							for signal in conrtol_lines:
								if signal in IN_OUT_LINES:
									byte = byte & IN_OUT_LINES[signal]

						ROM.write(address, byte)

				else:
					# Skip the JMP
					for step, conrtol_lines in enumerate(SKIP_JMP):
						address = instruction << 7 | flag_permutation << 4 | (step + 3)

						if ROM_NUM == 0:
							byte = 0
							for signal in conrtol_lines:
								if signal in CTRL_LINES:
									byte = byte | CTRL_LINES[signal]

							# Invert active low signals (ALU_OUT, HLT, NXT)
							byte = byte ^ 0b11100000

						else:
							# no In and OUT line is 0xff
							byte = 0xff
							for signal in conrtol_lines:
								if signal in IN_OUT_LINES:
									byte = byte & IN_OUT_LINES[signal]					

						ROM.write(address, byte)



	instruction_line = clean_line(file.readline(), file)
	micro_step_line = clean_line(file.readline(), file)

file.close()

ROM.cleanup()
