#!/usr/bin/python3
import sys

class CompilationError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

symbols = {}
instructions = {}

for line in sys.stdin:
	operands = line.split()
	if operands[1] == "=":
		if operands[0] in symbols:
			raise CompilationError("Duplicate definition of %s" % (operands[0]))
		symbols[operands[0]] = int(operands[2], 16)
	else:
		mem_position = int(operands[0], 16)
		if mem_position in instructions:
			raise CompilationError("Duplicate usage of %.4X" % (mem_position))
		instructions[mem_position] = operands[1:]

for position, instruction in sorted(instructions.items()):
	if len(instruction) == 1:
		print("%.4X %s" % (position, instruction[0]))
	else:
		if not instruction[1] in symbols:
			raise CompilationError("Undefined symbol %s" % (instruction[1]))
		print("%.4X %.4X" % (position, int(instruction[0], 16) + symbols[instruction[1]]))
