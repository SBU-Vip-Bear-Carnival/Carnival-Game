//
// carnival.ino — VIP BEAR accessible carnival game, V2.
//
// Arduino Mega 2560. Build it with the pinned toolchain, not the IDE's
// "whatever you happen to have installed":
//
//   arduino-cli compile --profile mega firmware/carnival
//
// Structure:
//   src/config/    pins, tuning, types      -- what the machine IS
//   src/hardware/  drivers for each device  -- how to talk to it
//   src/game/      modes and menu           -- what the game DOES
//
// This is the V2 skeleton. It brings the hardware up and compiles clean; the
// game logic is the Fall 2026 work. Add to it on a branch, never on main.
//

#include <Arduino.h>
#include <AccelStepper.h>
#include <FastLED.h>
#include <TMCStepper.h>

#include "src/config/pins.h"
#include "src/config/tuning.h"
#include "src/config/types.h"
#include "src/hardware/audio.h"

// --- Globals -----------------------------------------------------------
AccelStepper track1(AccelStepper::DRIVER, STEP_PIN1, DIR_PIN1);
AccelStepper track2(AccelStepper::DRIVER, STEP_PIN2, DIR_PIN2);

CRGB        leds[NUM_LEDS];
AudioSystem audio;
GameMode    currentMode = MODE_STANDBY;

// --- Setup -------------------------------------------------------------
void setup() {
  Serial.begin(115200);

  // DFPlayer Mini lives on Serial1 (Mega pins 18/19).
  Serial1.begin(9600);
  audio.begin(Serial1);

  pinMode(ENBL_PIN1, OUTPUT);
  pinMode(ENBL_PIN2, OUTPUT);
  digitalWrite(ENBL_PIN1, LOW);   // LOW = driver enabled on the TMC2209
  digitalWrite(ENBL_PIN2, LOW);

  pinMode(TRK1_LS1, INPUT_PULLUP);
  pinMode(TRK1_LS2, INPUT_PULLUP);
  pinMode(TRK2_LS1, INPUT_PULLUP);
  pinMode(TRK2_LS2, INPUT_PULLUP);

  pinMode(STRT_PIN,  INPUT_PULLUP);
  pinMode(START_LED, OUTPUT);
  pinMode(LED1,      OUTPUT);
  pinMode(LED2,      OUTPUT);

  track1.setMaxSpeed(MAX_STEPPER_SPEED);
  track1.setAcceleration(STEPPER_ACCELERATION);
  track2.setMaxSpeed(MAX_STEPPER_SPEED);
  track2.setAcceleration(STEPPER_ACCELERATION);

  FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
  FastLED.clear(true);

  Serial.println(F("carnival: ready"));
}

// --- Loop --------------------------------------------------------------
void loop() {
  switch (currentMode) {
    case MODE_STANDBY:      runStandby();     break;
    case MODE_SINGLE_EASY:  runSingleEasy();  break;
    case MODE_TWO_PLAYER:   runTwoPlayer();   break;
    case MODE_SINGLE_HARD:  runSingleHard();  break;
  }
}

// --- Mode stubs --------------------------------------------------------
// TODO(V2): implement against the TPU plates and the 5-button + LCD panel.
// Each of these should move into src/game/modes.h once it has real logic.

void runStandby() {
  // Idle attract pattern; wait for the start button.
}

void runSingleEasy() {
  // One player, one track. Each plate release advances one subdivision.
}

void runTwoPlayer() {
  // Both tracks race.
}

void runSingleHard() {
  // Like easy, but the track drifts backward between presses.
  // DRIFT_* in tuning.h is the accessibility knob -- see that file.
}
