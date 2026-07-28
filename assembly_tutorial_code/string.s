.globl main

.section .data
msg: .ascii "Hello,world!\n"

.section .text
main:
movq $1, %rax
movq $1, %rdi
leaq msg(%rip), %rsi
movq $13, %rdx
syscall
