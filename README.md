# hearts-textual
This is a silly little project to use [websockets](https://github.com/aaugustin/websockets) as the basis for a multiplayer hearts game server, and [textual](https://github.com/Textualize/textual) as the initial client for it.

# How To Use
```
git clone https://github.com/draggor/hearts-textual.git
cd hearts-textual

# Requires a python3.11 binary on your path
make install

# for server
make server

# for 1 - 4 clients
make client
```

## Requirements
- python3.11
- [poetry](https://python-poetry.org/)

# Design Goal
To generally us python typing, dataclasses, websockets, and textual to make a functioning multiplayer hearts game.  The TUI should allow full keyboard navigation but also use textual's mouse interactions, and allow keyboardless operation as well.

# High level TODO
- [x] Create a websocket server that runs forever, and allows clients to connect
- [x] Create a dumb client that can send/recieve JSON, and on the server side have it parse into the command schema for us
- [x] Have the client use the same command schema to parse server messages
- [ ] handle passwords and reconnects
  - [x] map Player instances to the websocket, and vice versa
  - [ ] using primitive passwords, allow rejoining
  - [ ] probably require unique usernames/validation
- [ ] THE RULES
  - [x] get points assigned to hearts and QC
  - [x] deal out a hand
  - [x] play cards one person at a time
  - [x] some rules maybe?
  - [x] continue to work on game loop turn order, out of turn can still happen
  - [ ] turn order being correctly written, but not being used/handled
- [ ] Create a textual TUI
  - [ ] renders your hand of cards
  - [ ] renders active plays
  - [ ] renders all necessary game state for a turn
  - [ ] way to check on / show full game state: score, rounds, etc
  - [ ] clock/turn timer for funsies?
  - [ ] keyboard bindings
  - [ ] mouse interactions
