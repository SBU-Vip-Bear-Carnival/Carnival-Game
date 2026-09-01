#pragma once
//
// pins.local.example.h — copy this to pins.local.h to override pins locally.
//
//   cp pins.local.example.h pins.local.h
//
// pins.local.h is gitignored. Nothing you put in it is ever committed, and CI
// never sees it. Define only the pins that differ on your bench; everything
// you leave out falls through to the real cabinet values in pins.h.
//
// Delete pins.local.h to go back to the cabinet's wiring.

// Example: your stepper is on different pins than the cabinet.
// #define STEP_PIN1  5
// #define DIR_PIN1   4

// Example: you have one plate on a Uno-style board.
// #define PRES1      A2
