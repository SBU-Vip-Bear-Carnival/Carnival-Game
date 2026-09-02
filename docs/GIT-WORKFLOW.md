# How we use git

You do not need to understand git to follow this. Copy the commands.

The rule that matters: **nobody commits to `main`.** You make a branch, you push
it, you open a pull request, someone glances at it, it merges. That is the whole
system. Everything below is detail.

---

## Why we bother

The previous version of this project lived in one repo with no rules. What
happened:

- `main` stopped compiling in May 2026 — a missing comma — and **nobody noticed
  for four months**, because nothing checked.
- Two people refactored in parallel and neither branch ever merged. The project
  ended up with two half-versions and no whole one.
- Someone made branches called `dummy_main` and `dummy_cleanup`, because they
  wanted somewhere safe to experiment and did not know a branch already is that.
- Three `wip/` branches sat untouched for six months and died there.

None of that was anyone being careless. It is what happens without guardrails.
Now there are guardrails.

---

## One-time setup

```bash
git clone https://github.com/SBU-Vip-Bear-Carnival/Carnival-Game.git
cd Carnival-Game
./tools/setup.sh
```

`setup.sh` checks you have `arduino-cli`, installs a hook that stops you pushing
to `main` by accident, creates your `tools/.env`, and then compiles the firmware
to prove the toolchain works. If it fails at that last step, stop and fix it —
you do not have a working setup yet.

---

## Every single time you work

**1. Start from an up-to-date `main`.**

```bash
git checkout main
git pull
```

**2. Make a branch. Name it `type/what-you-are-doing`.**

```bash
git checkout -b feat/audio-volume-buttons
```

Types: `feat` (new thing), `fix` (broken thing), `hw` (wiring/CAD), `docs`,
`test`, `chore`.

**3. Work. Commit as you go — small commits are good.**

```bash
git add .
git commit -m "Add volume up/down handling to the UI panel"
```

**4. Push it.**

```bash
git push -u origin feat/audio-volume-buttons
```

The first push on a branch needs `-u`. After that, just `git push`.

**5. Open a pull request.** GitHub prints a link when you push — click it. Fill
in the template. Say what you changed and whether you tested it on the cabinet.

**6. Wait for the build.** A robot compiles your branch. Green check = it
builds. Red X = it does not, and you need to fix it before anyone reviews.

**7. Get one approval, then squash-merge.** The branch deletes itself.

**8. Go back to step 1.** Your local `main` is now behind — pull before you
start the next thing.

---

## Writing a commit message

Say what changed and why it matters. Present tense.

Good:

```
Lower the plate threshold to 450 — the TPU prototype reads lower than PLA
Stop the track drifting during the grace period
Add the DFPlayer wiring diagram
```

Bad — all of these are real commits from the old repo:

```
puts the demo in the folder
Create lights folder
Update HEADER.md
```

The test: in six months, will someone scanning the log know whether this commit
is the one that broke the game? `Update HEADER.md` fails that test.

---

## When it goes wrong

This section exists so nobody ever needs a `dummy_main` again.

### "I want to throw away everything I just did"

Your branch is a scratch pad. Deleting it costs nothing and touches nobody.

```bash
git checkout main
git branch -D my-messy-branch          # local
git push origin --delete my-messy-branch   # if you already pushed it
```

`main` is untouched. This is what branches are *for* — experiment freely.

### "I want to undo my last commit but keep the code"

```bash
git reset --soft HEAD~1
```

Your changes are back to uncommitted. Edit, re-commit.

### "I want to throw away my uncommitted changes"

```bash
git restore .
```

⚠ This one really does delete work, and git cannot get it back. It is the only
command here that bites.

### "I committed to `main` by accident"

The hook should have stopped you, but if you got past it and have not pushed:

```bash
git branch my-work            # save it to a branch
git reset --hard origin/main  # put main back
git checkout my-work          # carry on properly
```

### "Someone else changed the same file — I have a conflict"

```bash
git checkout main
git pull
git checkout my-branch
git merge main
```

Git marks the clashes in the file like this:

```
<<<<<<< HEAD
your version
=======
their version
>>>>>>> main
```

Delete the `<<<<<<<`, `=======`, `>>>>>>>` lines and leave the code you want —
often a bit of both. Then:

```bash
git add .
git commit
```

**If you are not sure which version is right, ask the person who wrote the other
one.** Guessing here is how the old repo ended up with two half-versions.

### "My branch is really old and everything conflicts"

That is the actual lesson of the old `wip/` branches. **A branch older than about
two weeks should be merged or closed.** If it has drifted that far, it is usually
faster to start a fresh branch off current `main` and copy your changes in.

### "I broke something and I don't know what"

```bash
git log --oneline -10       # recent commits
git diff main               # everything your branch changed
```

Then ask. Nobody minds.

---

## Things you must not do

- **Never `git push --force` to `main`.** It rewrites history for everyone and
  can destroy other people's work. Force-pushing *your own* branch is fine.
- **Never commit `pins.local.h`.** It is your bench wiring. It is gitignored; if
  you force it in, CI will fail on purpose.
- **Never commit a fix you have not compiled.** That is precisely the four-month
  bug.

---

## Cheat sheet

| I want to… | Command |
|---|---|
| Start something new | `git checkout main && git pull && git checkout -b feat/thing` |
| See what I changed | `git status` and `git diff` |
| Save my work | `git add . && git commit -m "..."` |
| Send it up | `git push` (first time: `git push -u origin BRANCH`) |
| Which branch am I on? | `git branch --show-current` |
| Throw this branch away | `git checkout main && git branch -D BRANCH` |
| Undo last commit, keep code | `git reset --soft HEAD~1` |
| Build it | `arduino-cli compile --profile mega firmware/carnival` |
