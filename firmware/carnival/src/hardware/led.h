#pragma once
//
// Ported from V1's `cleanup` branch (main/src/led.h) on 2026-09-02,
// unchanged except for the include lines: V1 had one config.h, V2 splits it
// into config/pins.h, config/tuning.h and config/types.h.
//
#include <Arduino.h>

class MyLED {
public:
  MyLED(int pinNum) : pin(pinNum), state(false) {}

  void begin()   { pinMode(pin, OUTPUT); digitalWrite(pin, LOW); }
  void turnOn()  { digitalWrite(pin, HIGH); state = true;  }
  void turnOff() { digitalWrite(pin, LOW);  state = false; }
  void toggle()  { if (state) turnOff(); else turnOn(); }

private:
  int  pin;
  bool state;
};
