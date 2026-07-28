.globl main
.section .text
.extern print_int
main:
pushq %rbx
movq $0, %rbx

loop_start:
cmpq $10, %rbx
jg loop_end
movq %rbx, %rdi
callq print_int
addq $1, %rbx
jmp loop_start

loop_end:
movq $0, %rax
popq %rbx
retq

