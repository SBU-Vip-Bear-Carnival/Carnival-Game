#pragma once
//
// Ported from V1's `cleanup` branch (main/src/limit_switch.h) on 2026-09-02,
// unchanged except for the include lines: V1 had one config.h, V2 splits it
// into config/pins.h, config/tuning.h and config/types.h.
//
#include <Arduino.h>

class MyLimitSwitch {
public:
  MyLimitSwitch(int pinNum) : pin(pinNum), previousState(HIGH) {}

  void reinit() {
    pinMode(pin, INPUT_PULLUP);
    delay(50);
    previousState = digitalRead(pin);
  }

  // Returns true once on the HIGH→LOW edge.
  bool isPressed() {
    bool cur   = digitalRead(pin);
    bool fired = (previousState == HIGH && cur == LOW);
    previousState = cur;
    return fired;
  }

  bool isCurrentlyPressed() { return digitalRead(pin) == LOW; }

private:
  int  pin;
  bool previousState;
};
