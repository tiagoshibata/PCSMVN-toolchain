# PCSMVN toolchain

Toolchain básico para a máquina de PCS3616.

---

As ferramentas aqui são principalmente hacks rápidos juntados para as aulas. A
sintaxe do assembler pode mudar no futuro, algumas coisas foram feitas do jeito
mais simples para uma versão inicial. Se suprir minhas necessidades na aula eu
talvez deixe tudo assim mesmo, mas se continuarmos usando essa máquina nos labs
eu vou dar uma melhorada no tempo que sobrar do lab. Se ler o README estiver
muito massante, pule para os exemplos que dá para entender bem o funcionamento
vendo eles e o que tivemos em aula.

## Programas

O toolchain possui um programa principal (**pcsmvn**) responsável por chamar os
programas corretos. O pcsmvn detecta se o arquivo é um objeto ou fonte e realiza
linkagem ou compilação. Os programas não precisam ser chamados diretamente (o
pcsmvn deve deduzir o que chamar e a ordem sozinho).

* pcsmvn-pp: Pré-processador. O assembler é minimalista e um só recebe arquivos
com uma sintaxe bem restrita. O pré-processador gera um arquivo para o formato
certo (remove comentários, ajusta algumas operações...). Não é preciso chamá-lo
diretamente.

* pcsmvn-as: Assembler. Não é preciso chamá-lo diretamente.

* pcsmvn-ld: Linker. Não é preciso chamá-lo diretamente.

* pcsvnm-objdump: Dump de binários.

## Capacidades

Foi feito um assembler de código, com suporte a labels (rótulos de posição) e
resolução de símbolos na linkagem (pode se usar símbolos de outros objetos). Há
também um objdump que pode ser usado em arquivos compilados (\*.mvn fornecidos em
aula, por exemplo) ou objetos (\*.mvno gerados pelo compilador).

## Comandos

Os 16 comandos do processador estão inclusos com os seguintes mnemônicos:

**jmp (pulo incondicional), jz ou je (pulo se igual), jn (pulo se negativo),
mov (move imediato para AC), add (soma), sub (subtração), mul (multiplicação),
div (divisão), loa (load), sto (store), call (chamada de subrotina),
ret (retorno de subrotina), hlt (halt), in (entrada), out (saída),
sup (supervisor)**

A documentação deles está no material de aula. Todas com exceção de **ret**
recebem obrigatoriamente um operando, que pode ser um símbolo ou número
(hexadecimal, decimal ou binário). Além disso, foram criados os seguintes
comandos:

**dw**: Define Word - insere uma word (16 bits) na posição atual. Usada para
gerar constantes, por exemplo.

**func**: Gera o cabeçalho de uma função. Define uma label na posição e reserva
espaço para o endereço de retorno.

**[org] e [section]:** Definem a posição atual na memória. Usados para saber
onde compilar o programa e como calcular posições de labels. [org posição]
define a origem, posição a partir da qual serão calculados os endereços.
[section posição] define onde guardar o programa (para qual endereço será
compilado).

## Sintaxe

**;** indica comentários. Números em hexadecimal podem ser usados no notação
estilo Assembly (1234h) ou C (0x1234). Números começando em **0b** são vistos
como binários (eg. 0b10101). Números sem prefixo/sufixo são vistos como decimais.
O símbolo especial **$** representa a posição da intrução atual. Para cada
comando, basta colocar o mnemônico seguido de um ou mais espaços e o operando.
Labels podem ser definidas das seguintes maneiras:

* Antes de um dw:
```
label dw 0 ; define a label aqui e guarda 0 nessa posição
```

* Em qualquer linha com um **:**:
```
label: ; define a label aqui
```

* Com o comando **func**, que aloca o cabeçalho da função:
```
func formata_saida ; define formata_saida aqui e aloca espaço para o cabeçalho
```

## Exemplos

A pasta examples/ possui exemplos de uso. Em primeiro lugar, o primeiro programa
exemplo da aula é mostrado em seu equivalente em Assembly. O professor escolheu
colocar os dados antes do código, então temos que pular para a posição inicial
do código como primeira instrução.

```
jmp start
A dw -125	; A = -125.
B dw 100	; B = 100.
resultado dw 0	; buffer para o resultado.
start:
	loa A	; carrega A.
	add B	; soma B.
	sto resultado	; guarda em resultado.
	hlt $	; halt. Ao receber interrupção externa retorna para estado de halt.

```

O programa pcsmvn pode ser chamado com uma lista de fontes ou objetos e sem
flags adicionais para gerar um executável final ([basename do primeiro arquivo da
linha de comando].mvn). Chamar **pcsmvn add.asm** resulta em um arquivo **add.mvn**
com exatamente o mesmo conteúdo da aula (sem os comentários, claro):

```
0000 0008
0002 FF83
0004 0064
0006 0000
0008 8002
000A 4004
000C 9006
000E C00E
```

Além disso, podemos gerar objetos e linká-los depois. Os arquivos
symbol_resolution_main.asm e symbol_resolution_function.asm usam símbolos
definidos um no outro (as funções foram preenchidas com conteúdo qualquer):

symbol_resolution_main.asm:
```
[org 0]
[section 0]
mov -2
add 3
mul 5
dw 0xfffa
call teste_funcao
```

symbol_resolution_function.asm:
```
[org 0x200]
[section 0x200]
func teste_funcao
mov 123h
add 0x4
mul 5
dw 0xfffa
ret teste_funcao
```

Aqui escolhemos colocar o arquivo main na posição 0 e teste_funcao na 0x200 da
memória. org e section podem ser usados no meio do arquivo também e não apenas
no início. Se não forem definidos, o valor padrão é 0. Podemos compilar os 2 com
**pcsmvn symbol\_resolution\_\*** resulta em:

```
0000 3FFE
0002 4003
0004 6005
0006 FFFA
0008 A200
0200 0000
0202 3123
0204 4004
0206 6005
0208 FFFA
020A B000
```

Observa-se uma função gerada na posição 0, que chama a função definida em 0x200
(instrução A200). Não há conflito entre as posições de memória (se as funções
fossem se sobreescrever, haveria um erro na linkagem).

Para gerar objetos, use a flag **-c** como primeiro argumento. Por exemplo,
**pcsmvn -c symbol\_resolution\_function.asm** e
**pcsmvn -c symbol\_resolution\_main.asm** geram os arquivos
symbol_resolution_function.mvno e symbol_resolution_main.mvno. Eles podem ser
linkados no executável final com **pcsmvn symbol\_resolution\_\*.mvno**.

Por último, o programa pcsmvn-objdump gera dumps dos conteúdos (um dissasembly
do programa). Como não há distinção entre seções de dados e código, os dados
serão também mostrados como instruções:

pcsmvn-objdump prog1.mvn:
```
prog1.mvn
0000: jmp 0008
0002: sup 0F83
0004: jmp 0064
0006: jmp 0000
0008: loa 0002
000A: add 0004
000C: sto 0006
000E: hlt 000E
```

Em objetos, ele marca também a posição dos símbolos:

pcsmvn-objdump symbol_resolution_function.mvno:
```
symbol_resolution_function.mvno
0200: jmp 0000 ; symbol teste_funcao
0202: mov 0123
0204: add 0004
0206: mul 0005
0208: sup 0FFA
020A: ret 0200
```

## Bugs

Provavelmente. Os scripts foram testados em condições bem específicas (pastas e
arquivos sem espaços no nome e nada muito exótico). O que for encontrado de
errado pode ser postado aqui no GitHub mesmo.
