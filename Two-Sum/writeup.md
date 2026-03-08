# Writeup: Two Sum

## Introduction

The challenge description states that we must find two numbers n1 and n2 that satisfy the expression n1 > n1 + n2 OR n2 > n1 + n2. Obviously there are no numbers that exist that would satisfy that expression however because programs use integers that have a limited size we can overflow them to cause undefined behavior. In C integers have limited space because they are meant to fit into 32 bits with each combination of bits representing different numbers up to 2^31 - 1. If a number is larger than 2^31 - 1 then the number wraps around to negative numbers at first and then back to positive depending on how much larger the number is than 2^31 - 1. In other words the number becomes truncated to fit into the 32 bits resulting in a newer smaller number. So as long as the number is large enough then it should wrap around to being a positive number that is smaller than the original. This program also requires an integer overflow to continue onto testing the aforementioned expression (Note that the source code tests to see if n1 or n2 is greater than 0 this is the same as the expressions already mentioned just rearranged with simple algebra). Below is the relevant code in the source provided:

```
        if (scanf("%d", &num1) && scanf("%d", &num2)) {
            printf("You entered %d and %d\n", num1, num2);
            fflush(stdout);
            sum = num1 + num2;
            if (addIntOvf(sum, num1, num2) == 0) {
                printf("No overflow\n");
                fflush(stdout);
                exit(0);
            } else if (addIntOvf(sum, num1, num2) == -1) {
                printf("You have an integer overflow\n");
                fflush(stdout);
            }

            if (num1 > 0 || num2 > 0) {
                flag = fopen("flag.txt","r");
                if(flag == NULL){
                    printf("flag not found: please run this on the server\n");
                    fflush(stdout);
                    exit(0);
                }
                char buf[60];
                fgets(buf, 59, flag);
                printf("YOUR FLAG IS: %s\n", buf);
                fflush(stdout);
                exit(0);
            }
        }
``` 

## Result

All that is left is to test the theory and get the flag. Below is the result of overflowing both integers.

```
    n1 > n1 + n2 OR n2 > n1 + n2
    What two positive numbers can make this possible:
    500000000000000
    500000000000000
    You entered 1382236160 and 1382236160
    You have an integer overflow
    YOUR FLAG IS: picoCTF{Tw0_Sum_Integer_Bu773R_0v3rfl0w_e06700c0}
```

Finally, we have our flag. As I mentioned before the reason 500000000000000 becomes 1382236160 is because when a number is too large to fit into the 32 bits assigned to each integer the number gets truncated and the value wraps around to, in this case, 1382236160.

