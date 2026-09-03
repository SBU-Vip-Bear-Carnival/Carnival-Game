#pragma once
//
// pins.local.example.h — your bench wiring, not the cabinet's.
//
// SETUP (once):
//
//   cd firmware/carnival/src/config
//   cp pins.local.example.h pins.local.h
//
// Then uncomment the lines you need and put YOUR pin numbers on them.
//
// HOW IT WORKS
//
// Every pin in pins.h is wrapped in #ifndef, and pins.h includes this file
// first when it exists. So anything you define here wins, and anything you
// leave commented falls through to the cabinet's real value. You override the
// three pins that differ on your breadboard, not all twenty-three.
//
// pins.local.h is gitignored. It can never be committed, CI never sees it, and
// deleting it puts you straight back on the cabinet's wiring. If you want to
// know what the machine really is, read pins.h -- not this file.
//
// ⚠ Do NOT edit pins.h to make your bench work. That file means "the cabinet
// changed," and committing your breadboard into it is exactly how V1 kept
// overwriting the real wiring.
//
// The values shown commented out below are the CABINET's current values, so
// you can see what you are changing away from.
//

// =========================================================================
// Steppers
// =========================================================================
// #define STEP_PIN1   3
// #define DIR_PIN1    2
// #define ENBL_PIN1   7

// #define STEP_PIN2   9
// #define DIR_PIN2    8
// #define ENBL_PIN2   13    // ⚠ 13 is the built-in LED pin -- see docs/HARDWARE.md

// =========================================================================
// Pressure plates  (analog pins only -- these are read with analogRead)
// =========================================================================
// #define PRES1       A0
// #define PRES2       A1

// =========================================================================
// Limit switches  (INPUT_PULLUP, switch shorts to GND)
// =========================================================================
// #define TRK1_LS1    25    // track 1, start
// #define TRK1_LS2    23    // track 1, end
// #define TRK2_LS1    29    // track 2, start
// #define TRK2_LS2    27    // track 2, end

// =========================================================================
// Start button and indicator LEDs
// =========================================================================
// #define STRT_PIN    48
// #define START_LED   53
// #define LED1        45
// #define LED2        37

// =========================================================================
// Addressable strip
// =========================================================================
// #define DATA_PIN    6     // WS2812B data line

// =========================================================================
// LCD — parallel HD44780, 4-bit mode
// =========================================================================
// ⚠ These are ARDUINO pin numbers. The LCD module has its own, different
// numbering, and the two collide in conversation. The comment on each line is
// the module pin it goes to. See docs/decisions/0002-ui-panel-wiring.md.
//
// #define LCD_RS      30    // -> module pin 4
// #define LCD_EN      31    // -> module pin 6
// #define LCD_D4      32    // -> module pin 11
// #define LCD_D5      33    // -> module pin 12
// #define LCD_D6      34    // -> module pin 13
// #define LCD_D7      35    // -> module pin 14

// =========================================================================
// UI panel buttons  (INPUT_PULLUP, other leg to GND)
// =========================================================================
// #define BTN_UP      40
// #define BTN_DOWN    41
// #define BTN_SELECT  42
// #define BTN_BACK    43
// #define BTN_START   44

// =========================================================================
// Worked example — testing two plates on a Uno-style board
// =========================================================================
// You have no second track, one plate on a different analog pin, and your
// stepper on different pins. Three lines:
//
//   #define STEP_PIN1  5
//   #define DIR_PIN1   4
//   #define PRES1      A2
//
// Everything else -- limit switches, LEDs, the strip, the panel -- stays on
// the cabinet's values, which is what you want. You are only changing what is
// physically different in front of you.
