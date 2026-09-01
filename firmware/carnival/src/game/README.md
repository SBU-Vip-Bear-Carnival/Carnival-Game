# Game logic

Modes and menu. What the game *does*, as opposed to `../hardware/`, which is how
to talk to a device.

Planned:

- `modes.h` — the four game modes, moved out of `carnival.ino` once they have
  real logic
- `menu.h` — the 5-button and LCD menu (V2)

Two rules:

- **Nothing here calls `delay()`.** A blocked loop misses a plate press, and to
  a player that reads as the game ignoring them. Check state and return.
- **Each mode owns its state struct** in `../config/types.h` and resets it
  through `reset()`, so a mode always starts clean.
