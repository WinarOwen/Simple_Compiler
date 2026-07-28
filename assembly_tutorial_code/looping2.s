.globl main
.section .text
main:
movq $60, %rax
movq $20 , %rdi

start_loop:
cmpq $0, %rdi
jle end_loop
subq $2, %rdi
jmp start_loop

end_loop:
syscall


