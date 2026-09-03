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
#include <TMCStepper.h>   // pinned and installed, but no driver is constructed
                          // yet -- see the TMC block in src/config/tuning.h

#include "src/config/pins.h"
#include "src/config/tuning.h"
#include "src/config/types.h"
#include "src/hardware/audio.h"
#include "src/hardware/button.h"
#include "src/hardware/led.h"
#include "src/hardware/lightstrip.h"
#include "src/hardware/limit_switch.h"
#include "src/hardware/pressure_plate.h"
#include "src/hardware/track.h"

// --- Globals -----------------------------------------------------------
CRGB        leds[NUM_LEDS];        // MyLightstrip writes through this, via extern
AudioSystem audio;
GameMode    currentMode = MODE_STANDBY;

MyButton        startButton(STRT_PIN);
MyLED           statusLED(START_LED);
MyLED           led1(LED1);
MyLED           led2(LED2);
MyLightstrip    lightStrip;
MyPressureplate pressurePlate1(PRES1);
MyPressureplate pressurePlate2(PRES2);

// ⚠ MyTrack is NOT constructed yet, on purpose.
//
// Its constructor wants a HardwareSerial* for the TMC2209's UART. V1 handed it
// Serial1 and Serial2; V2 has already given Serial1 to the DFPlayer. Picking a
// port here would bury a wiring decision inside a port commit, so the two
// tracks arrive in the hw/uart-split PR along with the wire that has to move.
//
// The bare AccelStepper globals V1 never had are gone with them -- MyTrack owns
// its own stepper, and two objects driving one motor is worse than none.

// --- Setup -------------------------------------------------------------
void setup() {
  Serial.begin(115200);

  // DFPlayer Mini lives on Serial1 (Mega pins 18/19).
  Serial1.begin(9600);
  audio.begin(Serial1);

  // Each object sets up its own pins in begin(). The loose pinMode() calls that
  // used to live here are gone -- two places configuring one pin is how they
  // drift apart.
  startButton.begin();
  statusLED.begin();
  led1.begin();
  led2.begin();
  pressurePlate1.begin();
  pressurePlate2.begin();

  // ⚠ FastLED.addLeds() lives in MyLightstrip::begin() and MUST NOT also be
  // called here -- registering the same strip twice makes FastLED write it
  // twice on every show(), which costs time and flickers.
  lightStrip.begin();

  // Limit switch and ENABLE pins are configured by MyTrack::begin(), which
  // arrives with the tracks in hw/uart-split.

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
