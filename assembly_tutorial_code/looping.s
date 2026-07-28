.globl main

.section .text
main:
movq $60, %rax
movq $0, %rdi

start_loop:
cmpq $10, %rdi
jge end_loop
addq $2, %rdi
jmp start_loop

end_loop:
syscall 

