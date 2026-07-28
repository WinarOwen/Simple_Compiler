.globl main

.section .text

main:
movq $4, %rdi
movq $5 , %rsi
movq $6, %rdx
callq sum3
movq %rax, %rdi
movq $60, %rax
syscall




sum3:
pushq %rbp
movq %rsp, %rbp
subq $8, %rsp

movq %rdi, %rax
addq %rsi, %rax
movq %rax, -8(%rbp)
movq %rdx, %rax
addq -8(%rbp), %rax

movq %rbp, %rsp
popq %rbp
retq

