# Writeup: Baby Game

## Introduction

This challenge is a game that allows you to move a piece around a board with the goal of reach the x at the bottom left corner of the board. You can move with the characters w, a, s, and d. Their directions are self explanatory if you have ever used a keyboard when gaming. While messing with the controls I was able to figure out that typing out l and any character you can change the appearance of the character and when you send the input p the solve round function is called which moves your character to the required position to win the game. The game also presents your position and a value that represents whether you have gotten the flag or not. This challenge only gives you access to the binary not the source so in order to figure out what is happening under the hood we have to use gdb to disassemble each function in the binary to help us understand how the game works.

## Dissasembly

Below is all of the relevant code dissassembled and translated from assembly to C code to make it easier to understand:

### Main

```
        int main() {
            char player[0xaa4];
            char map[0xa98];
            char input;
    
            init_player(player);
            init_map(map, player);
            print_map(map, player);
    
            signal(2, handler);
    
            while (1) {
                input = getchar();
                move_player(player, input, map);
                print_map(map, player);
        
                if (player[0] == 0x1d && player[1] == 0x59) {
                    puts("You win!");
                    if (player[2] != 0) {
                        puts("Cheater!");
                        win();
                        fflush(stdout);
                    }
                } else {
                    continue;
                }
                break;
            }
    
            return 0;
        }
```

### move_player

```
    void move_player(int *player, char input, char *map) {
        char move = (char)input;
    
        if (move == 'l') {
            char c = getchar();
            player_char = c;
        }
    
        if (move == 'p') {
            solve_round(player, map);
        }
    
        map[player[0] * 0x5a + player[1]] = '.';
    
        if (move == 'w') {
            player[0]--;
        } else if (move == 's') {
            player[0]++;
        } else if (move == 'a') {
            player[1]--;
        } else if (move == 'd') {
            player[1]++;
        }
    
        map[player[0] * 0x5a + player[1]] = player_char;
    }
```

### solve_round

```
    void solve_round(int *player, char *map) {
        while (player[1] != 0x59) {
            if (player[1] <= 0x58) {
                move_player(player, 'd', map);
            } else {
                move_player(player, 'a', map);
            }
            print_map(player, map);
        }

        while (player[0] != 0x1d) {
            if (player[0] <= 0x1c) {
                move_player(player, 'w', map);
            } else {
                move_player(player, 's', map);
            }
            print_map(player, map);
        }

        sleep(0);

        if (player[0] == 0x1d && player[1] == 0x59) {
            puts("You win!");
        }
    }
```

## Code Analysis

In the main function we can see that to win we must change player[2]'s value to any value other than 0. Since there is no bounds checking on the map position it follows that we can move around in memory out of bounds to the player[2] variable and overwrite the value there allowing us to obtain the flag.

`map[player[0] * 0x5a + player[1]] = player_char;`

I am not sure where the player 2 variable is located, but we can brute force a solution by trying to go out of bounds backwards out of the map array or forwards. After a bit of trial and error I figured out that I could move backwards and change the value of the player[2] value. Once the value on screen has changed next to "Player has flag:" I can just press p and get transported to the winning tile and thus win the game. 

```
    Player position: 29 89
    Player has flag: 46
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    ..........................................................................................
    .........................................................................................@
    You win!
    flage
    picoCTF{gamer_m0d3_enabled_f3416ca2}    
```
Finally we are able to obtain the flag!

