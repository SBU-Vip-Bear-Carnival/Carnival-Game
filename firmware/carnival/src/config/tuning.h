#pragma once
//
// tuning.h — calibration for the physical cabinet.
//
// This file IS committed, deliberately. There is one machine, and a threshold
// that only exists on one person's laptop is how the game stops working the
// week they are away. Change a value here, open a PR, say what you measured.
//
// If a number in here is wrong, the game feels wrong. Treat it as real code.
//

// --- TMC2209 stepper drivers -------------------------------------------
const float TMC_R_SENSE          = 0.11f;   // sense resistor on the driver board
const int   TMC_CURRENT_MA       = 600;     // per-motor RMS current
const int   TMC_MICROSTEPS       = 2;

// --- Motion ------------------------------------------------------------
const int   MAX_STEPPER_SPEED    = 2000;
const int   STEPPER_ACCELERATION = 1000;
const int   NORMAL_SPEED         = 1000;
const int   SLOW_SPEED           = 400;
const int   BOUNDS_SPEED         = 800;     // speed while seeking a limit switch

// --- Pressure plates ---------------------------------------------------
// PRESSURE_THRESHOLD is the accessibility-critical number. Too high and a
// child who cannot press hard cannot play at all. Re-measure it whenever the
// plate material changes -- TPU and PLA do not read the same.
const int           PRESSURE_THRESHOLD = 500;
const unsigned long PLATE_DEBOUNCE_MS  = 50;
const unsigned long PLATE_MIN_PRESS_MS = 250;   // ignore brushes and stumbles

// --- Track -------------------------------------------------------------
const int           TRACK_SUBDIVISIONS     = 5;    // presses needed to win
const unsigned long CALIBRATION_TIMEOUT_MS = 15000;

// --- Mode 3 backward drift ---------------------------------------------
// This is the difficulty knob for the whole game. Raising DRIFT_SPEED or
// DRIFT_STEPS_PER_INTERVAL makes Mode 3 harder; DRIFT_GRACE_PERIOD_MS is how
// long a player gets after a press before the track starts pulling back.
const int           DRIFT_SPEED              = 200;
const int           DRIFT_INTERVAL_MS        = 500;
const int           DRIFT_STEPS_PER_INTERVAL = 100;
const unsigned long DRIFT_GRACE_PERIOD_MS    = 1000;

// --- Lighting ----------------------------------------------------------
const int   NUM_LEDS = 40;
