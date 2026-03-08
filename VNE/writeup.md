# Writeup: VNE

## Introduction

For this challenge we will be taking advantage of the command injection vulnerability which occurs when a binary uses an environment variable to construct a shell command without sanitizing the input. We do not have access to the binary on our own machine nor do we have access to the source code. When we try to run the command we get the following error:
`Error: SECRET_DIR environment variable is not set`

My intuition tells me we can set this variable by using the export command. Since the variable contained in the error is referred to as a secret directory I set the SECRET_DIR variable to root and then run the program to see what it does. The result of doing this is shown below:

```
    Listing the content of /root/flag.txt as root:
    /root/flag.txt    
```

## Results

As you can see it is listing the contents of the directory which I placed in the SECRET_DIR variable and it shows us that there is a flag that located in the folder. Since the program is using the ls command I assume that it is using the system call function which means I can probably pass other system commands through the export variable. My first thought is to pass in the cat command to the SECRET_DIR variable and then run the binary to show the contents of flag.txt. Below is the result of doing that:

```
    ctf-player@pico-chall$ export SECRET_DIR="/root;cat /root/flag.txt"
    ctf-player@pico-chall$ ./bin
    Listing the content of /root;cat /root/flag.txt as root:
    flag.txt
    picoCTF{Power_t0_man!pul4t3_3nv_1670f174}
```

And there we have it, the flag was printed as a result of passing the cat command into the SECRET_DIR variable. If you notice the way that I pass in the cat command is by separating the ls command from the cat command with a semicolon, that is because terminal commands can be written all on one line if you so choose to write them that way by seperating them with a semicolon meaning you can pass in as many commands as you want to the system function call.
