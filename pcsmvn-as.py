#!/usr/bin/python3
import sys

opcodes = {"jmp" : 0 << 12, "jz" : 1 << 12, "je" : 1 << 12, "jn" : 2 << 12,
	"jl" : 2 << 12, "mov" : 3 << 12, "add" : 4 << 12, "cmp" : 5 << 12,
	"sub" : 5 << 12, "mul" : 6 << 12, "div" : 7 << 12, "loa" : 8 << 12,
	"sto" : 9 << 12, "call" : 0xa << 12, "ret" : 0xb << 12, "hlt" : 0xc << 12,
	"in" : 0xd << 12, "out" : 0xe << 12, "sup" : 0xf << 12}

symbols = {}

class CompilationError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def do_parse_number(number):
	number = number.lower()
	if len(number) >= 2:
		if number[0:2] == "0x":
			return int(number[2:], 16)
		if number[-1] == "h":
			return int(number[:-1], 16)
		if number[0:2] == "0b":
			return int(number[2:], 2)
	return int(number)

def parse_number(number, mask=0xfff):
	if number == "$":
		return org
	if not (number[0].isdecimal() or (number[0] == "-" and number[1].isdecimal())):
		return None
	if number[0] == "-":
		n = do_parse_number(number[1:])
		n = (n ^ mask) + 1
	else:
		n = do_parse_number(number)
	return n & mask

org = 0
section = 0
for line in sys.stdin:
	operands = line.split()
	if len(operands) != 2:
		raise CompilationError("Invalid %s" % (line))
	operation = operands[0].lower()
	operand = operands[1]
	if operand == ":":	# label
		if operands[0] in symbols:
			raise CompilationError("Duplicate definition of %s" % (operands[0]))
		symbols[operands[0]] = org
	elif operation[0] == "[" and operand[-1] == "]":
		if operation == "[org":
			org = parse_number(operand[:-1])
			if org == None:
				raise CompilationError("Invalid %s" % (line))
		elif operation == "[section":
			section = parse_number(operand[:-1])
			if section == None:
				raise CompilationError("Invalid %s" % (line))
		else:
			raise CompilationError("Invalid %s" % (line))
	else:
		if not operation in opcodes:
			if operation == "dw":
				operand_value = parse_number(operand, 0xffff)
				if operand_value == None:
					print("%.4X %.4X %s" % (section, 0, operand))
				else:
					print("%.4X %.4X" % (section, operand_value))
				org += 2
				section += 2
			# elif operation == "db":
			# 	operand_value = parse_number(operand, 0xff)
			# 	if operand_value == None:
			# 		print("%.4X %.4X %s" % (section, 0, operand))
			# 	else:
			# 		print("%.4X %.4X" % (section, operand_value))
			# 	org += 1
			# 	section += 1
			else:
				raise CompilationError("Unknown instruction %s" % (operation))
		else:
			opcode = opcodes[operation]
			operand_value = parse_number(operand)
			if operand_value == None:
				print("%.4X %.4X %s" % (section, opcode, operand))
			else:
				print("%.4X %.4X" % (section, opcode | operand_value))
			org += 2
			section += 2

for key, value in symbols.items():
	print("%s = %.4X" % (key, value))
