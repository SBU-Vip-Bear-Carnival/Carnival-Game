# Getting the code onto the game

"Flashing" or "uploading" means copying the compiled program onto the Arduino.
The Arduino only runs what was last uploaded to it — editing a file on your
laptop changes nothing until you do this.

**You do not need the Arduino IDE.** You do not need to know how any of it works
to follow this page. Copy the commands.

---

## First time only

**1. Install `arduino-cli`.**

```bash
brew install arduino-cli          # macOS
```

Windows or Linux: https://arduino.github.io/arduino-cli/latest/installation/

**2. Run the setup script from the project folder.**

```bash
./tools/setup.sh
```

It installs the exact board core and libraries this project is pinned to,
creates your `tools/.env`, installs a git hook that stops you pushing to `main`
by accident, and then compiles the firmware to prove it all works.

**If it fails at the compile step, stop.** You do not have a working setup yet,
and uploading is not going to go better than compiling did.

**3. Plug the Arduino in and find its port.**

```bash
arduino-cli board list
```

You get something like:

```
Port                            Type              Board Name
/dev/cu.usbmodem14201           Serial Port (USB) Arduino Mega 2560
```

Copy that port. Open `tools/.env` and put it on the `SERIAL_PORT` line:

```
SERIAL_PORT=/dev/cu.usbmodem14201
```

Your port will not match anyone else's, which is exactly why `tools/.env` is
gitignored. Do not commit it.

| System | Looks like |
|---|---|
| macOS | `/dev/cu.usbmodem14201` |
| Linux | `/dev/ttyACM0` |
| Windows | `COM3` |

---

## Every time after that

```bash
./tools/flash.sh
```

That compiles and uploads in one step. When it prints `Done.` the game is
running the new code — the board restarts on its own.

If you only want to check that your code builds, without a board plugged in:

```bash
arduino-cli compile --profile mega firmware/carnival
```

This is the same command the robot runs on your pull request, so if it passes
here it passes there.

---

## Watching what the game is thinking

The firmware prints what it is doing. To read it:

```bash
arduino-cli monitor -p /dev/cu.usbmodem14201 -c baudrate=115200
```

Use your own port. **The baud rate must be 115200** or you get gibberish.

Once the game is running you can type single letters into that window to ask it
questions:

| key | tells you |
|---|---|
| `p` | raw pressure plate readings — **this is how you set the plate threshold** |
| `l` | all four limit switches, HIT or open |
| `b` | whether the start button is pressed |
| `1` / `2` | where track 1 / track 2 currently is |
| `m` | which game mode it is in |
| `h` | this list |

⚠ **Only one program can hold the serial port at a time.** If the monitor is
open, `flash.sh` will fail to upload. Close the monitor first — `Ctrl-C`.

---

## When it goes wrong

### "No board at /dev/…"

The port changed. It often does when you unplug and replug, or use a different
USB socket. Run `arduino-cli board list` again and update `tools/.env`.

### It uploads, but the game does nothing

Open the monitor. If you see `carnival: ready`, the code is running and the
problem is wiring, not software. Use `l` and `p` to check the switches and
plates individually.

### Motor 2 twitches when I upload

**That one is expected.** `ENBL_PIN2` is on pin 13, which is also the board's
built-in LED. The bootloader blinks that LED on every reset and upload, and the
driver reads the blink as an enable pulse. It is a known V1 inheritance, written
up in [`HARDWARE.md`](HARDWARE.md). Do not go looking for it in the code.

### "Permission denied" on the port (Linux)

```bash
sudo usermod -a -G dialout $USER
```

Then log out and back in.

### It compiled yesterday and does not today

Someone probably added a library. Pull `main` and run `./tools/setup.sh` again —
it installs whatever `sketch.yaml` now pins.

---

## Testing on your own breadboard

If your bench wiring is not the cabinet's, **do not edit `pins.h`.** That file
means "the cabinet changed."

```bash
cd firmware/carnival/src/config
cp pins.local.example.h pins.local.h
```

Uncomment the pins that are different for you and put your own numbers on them.
Everything you leave alone falls through to the cabinet's real values. The file
is gitignored, so it cannot break the machine for anyone else, and deleting it
puts you back on the real wiring.

---

## The rule that matters

**Never upload code you have not compiled, and never merge code you have not
uploaded.** V1's `main` branch did not compile for four months because a comma
was missing and nobody checked. The compile step is thirty seconds.
