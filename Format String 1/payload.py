from pwn import *

def hex_to_str(val, num_bytes, endian='little'):
    b = val.to_bytes(num_bytes, endian)
    return ''.join(chr(x) if 32 <= x < 127 else '.' for x in b)

# Add your hex values and byte counts here
data = [
    (0x7b4654436f636970, 8),
    (0x355f31346d316e34, 8),
    (0x3478345f33317937, 8),
    (0x65355f673431665f, 8),
    (0x7d346263623736, 8)
    ]

for val, n in data:
    print(f'{hex(val)} -> {hex_to_str(val, n)}')

# Or print all together as one string
print(''.join(hex_to_str(v, n) for v, n in data))
