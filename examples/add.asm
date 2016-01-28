jmp start
A dw -125
B dw 100
resultado dw 0
start:
	loa A
	add B
	sto resultado
	hlt $
