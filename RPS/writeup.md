# Writeup: RPS

## Introduction

Looking over the code provided by this challenge I can see that in order to obtain the flag we need to win the game 5 times and that the win condition is met if the input string contains the winning choice. This happens because the strstr function checks to see if the string exists as a substring within the target string.

## Relevant Line of Code

`if (strstr(player_turn, loses[computer_turn]))`

## Result

This means I can send a string that contains all choices and win every time. The following output is a result of sending all three choices 5 times giving me the flag:

```
    Welcome challenger to the game of Rock, Paper, Scissors
    For anyone that beats me 5 times in a row, I will offer up a flag I found
    Are you ready?
    Type '1' to play a game
    Type '2' to exit the program
    1
    1


    Please make your selection (rock/paper/scissors):
    rockpaperscissors
    rockpaperscissors
    You played: rockpaperscissors
    The computer played: scissors
    You win! Play again?
    Type '1' to play a game
    Type '2' to exit the program
    rockpaperscissors
    rockpaperscissors
    Please put in a valid number
    Type '1' to play a game
    Type '2' to exit the program
    Please put in a valid number
    Type '1' to play a game
    Type '2' to exit the program
    Please put in a valid number
    Type '1' to play a game
    Type '2' to exit the program
    Please put in a valid number
    Type '1' to play a game
    Type '2' to exit the program
    Please put in a valid number
    Type '1' to play a game
    Type '2' to exit the program
    Please put in a valid number
    Type '1' to play a game
    Type '2' to exit the program
    Please put in a valid number
    Type '1' to play a game
    Type '2' to exit the program
    Please put in a valid number
    Type '1' to play a game
    Type '2' to exit the program
    Please put in a valid number
    Type '1' to play a game
    Type '2' to exit the program
    1
    1


    Please make your selection (rock/paper/scissors):
    rockpaperscissors
    rockpaperscissors
    You played: rockpaperscissors
    The computer played: scissors
    You win! Play again?
    Type '1' to play a game
    Type '2' to exit the program
    1
    1


    Please make your selection (rock/paper/scissors):
    rockpaperscissors
    rockpaperscissors
    You played: rockpaperscissors
    The computer played: paper
    You win! Play again?
    Type '1' to play a game
    Type '2' to exit the program
    1
    1


    Please make your selection (rock/paper/scissors):
    rockpaperscissors
    rockpaperscissors
    You played: rockpaperscissors
    The computer played: scissors
    You win! Play again?
    Type '1' to play a game
    Type '2' to exit the program
    1
    1


    Please make your selection (rock/paper/scissors):
    rockpaperscissors
    rockpaperscissors
    You played: rockpaperscissors
    The computer played: rock
    You win! Play again?
    Congrats, here's the flag!
    picoCTF{50M3_3X7R3M3_1UCK_B69E01B8}
    Type '1' to play a game
    Type '2' to exit the program
    2
    2

```
