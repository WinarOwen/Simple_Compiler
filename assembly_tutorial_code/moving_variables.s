.globl main

.section .data
x: .quad 5
y: .quad 7

.section .text
main:
movq $60, %rax
movq x(%rip), %rdi
addq y(%rip), %rdi
syscall
