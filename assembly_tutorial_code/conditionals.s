.globl main


.section .text
main:
movq $60, %rax
movq $10, %rdi
movq $9, %rcx
cmpq %rcx, %rdi
jge end_block
movq $0, %rdi

end_block:
syscall

