	.globl main
main:
    pushq %rbp
    movq %rsp, %rbp
    subq $48, %rsp
    movq $30, %rax
    addq $20, %rax
    movq %rax, -8(%rbp)
    movq $98, %rax
    negq %rax
    movq %rax, -16(%rbp)
    movq -8(%rbp), %rax
    addq -16(%rbp), %rax
    movq %rax, -24(%rbp)
    movq $34, -32(%rbp)
    movq -24(%rbp), %rax
    addq %rax, -32(%rbp)
    callq read_int
    movq %rax, -40(%rbp)
    movq -32(%rbp), %rax
    addq -40(%rbp), %rax
    movq %rax, -48(%rbp)
    movq -48(%rbp), %rdi
    callq print_int
    addq $48, %rsp
    popq %rbp
    retq 

