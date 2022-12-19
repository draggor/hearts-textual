# hearts-textual
This is a silly little project to use [websockets](https://github.com/aaugustin/websockets) as the basis for a multiplayer hearts game server, and [textual](https://github.com/Textualize/textual) as the initial client for it.

# Design Goal
To generally us python typing, dataclasses, websockets, and textual to make a functioning multiplayer hearts game.  The TUI should allow full keyboard navigation but also use textual's mouse interactions, and allow keyboardless operation as well.

# High level TODO
- [x] Create a websocket server that runs forever, and allows clients to connect
- [x] Create a dumb client that can send/recieve JSON, and on the server side have it parse into the command schema for us
- [ ] Have the client use the same command schema to parse server messages
- [ ] THE RULES
  - [ ] get points assigned to hearts and QC
  - [ ] deal out a hand
  - [ ] play cards one person at a time
  - [ ] some rules maybe?
  - [ ] If not rules, undo is a requirement
- [ ] Create a textual TUI
  - [ ] renders your hand of cards
  - [ ] renders active plays
  - [ ] renders all necessary game state for a turn
  - [ ] way to check on / show full game state: score, rounds, etc
  - [ ] clock/turn timer for funsies?
  - [ ] keyboard bindings
  - [ ] mouse interactions
