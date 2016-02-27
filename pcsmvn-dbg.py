#!/usr/bin/python3

# Feito para ser executado com um pipe (eg. mkfifo /tmp/pcsmvn-dbg-pipe) e receber
# linhas do simulador (eg. pcsmvn-dbg.py < /tmp/pcsmvn-dbg-pipe em um terminal e
# rlwrap java -jar mvn.jar | tee /tmp/pcsmvn-dbg-pipe em outro).

import sys

opcodes = ["jmp", "jz", "jn", "mov", "add", "sub", "mul", "div", "loa", "sto",
	"call", "ret", "hlt", "in", "out", "sup"]

while True:
	line = ''
	# Pára em \n ou : (da pergunta "Continua (s/n)[s]:")
	while not line.endswith('\n') and not line.endswith(':') and not line.endswith('\0'):
		c = sys.stdin.read(1)
		if not c:
			sys.exit(0)
		line += c
	line = line.split()
	try:
		if len(line) >= 7:
			position = int(line[0], 16)
			opcode = opcodes[int(line[4], 16)]
			operand = int(line[5], 16)
			ac = int(line[6], 16)
			print('%.4x %s %.4x\t\tAC = %.4x' % (position, opcode, operand, ac))
	except ValueError as e:
		pass
