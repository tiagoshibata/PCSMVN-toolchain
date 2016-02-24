#!/usr/bin/python3
import sys

opcodes = ["jmp", "jz", "jn", "mov", "add", "sub", "mul", "div", "loa", "sto",
	"call", "ret", "hlt", "in", "out", "sup"]

memory = {}
symbols = {}
for input_line in sys.stdin:
	input_line = input_line.split(';')
	if len(input_line) > 1:
		comments = ';'.join(input_line[1:])[:-1]
	else:
		comments = ''
	line = input_line[0]
	if not line:
		print("; %s" % (comments))
		continue
	operands = line.split()
	if operands[1] == "=":	# label
		symbols[operands[0]] = int(operands[2], 16)
		continue
	position = int(operands[0], 16)
	word = int(operands[1], 16)
	operation = word >> 12
	operand = word & 0xfff
	asm_line = opcodes[operation] + " "
	if len(operands) == 2:
		asm_line += "%.4X ; %s" % (operand, comments)
	else:
		if operand == 0:
			asm_line += operands[2]
		else:
			asm_line += "%.4X + %s" % (operand, operands[2])
	memory[position] = asm_line

for symbol, position in symbols.items():
	if position in memory:
		memory[position] += " ; symbol %s" % (symbol)
	else:
		memory[position] = " ; symbol %s" % (symbol)

for key, value in sorted(memory.items()):
	print("%.4X: %s" % (key, value))
